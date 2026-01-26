"""
LiveKit AI Interviewer Agent Server.

Main entry point for the LiveKit agent.
"""
import logging
import asyncio
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentServer, AgentSession, Agent, JobProcess
from livekit.agents import ConversationItemAddedEvent, UserInputTranscribedEvent
from livekit.plugins import google, silero, cartesia
from sqlalchemy import select

from app.services.core.database import AsyncSessionLocal
from app.models.interview import InterviewSession
from config.settings import get_settings
from app.agents.transcript import TranscriptManager
# ============================================
# LAZY IMPORTS for faster subprocess startup
# ============================================
# These modules import heavy dependencies (Google Gemini SDK, etc.)
# Moving to lazy imports to avoid reloading in spawned subprocesses
#
# DO NOT import at module level:
# - prompt_manager, shadow_monitor, observability
# - candidate_profile_manager, scoring_engine, difficulty_adapter
# - competency_evaluator, cross_stage_memory, question_generator
#
# Instead, import inside functions when needed

load_dotenv()

# Get settings
settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interview-agent")


class InterviewAssistant(Agent):
    """Custom agent that follows interviewer instructions."""
    
    def __init__(self, instructions: str) -> None:
        super().__init__(instructions=instructions)


# ============================================
# CLOUD RUN OPTIMIZED SERVER CONFIGURATION
# ============================================
# Key optimizations for Cloud Run:
# 1. initialize_process_timeout: Default 10s is too short for cold starts
# 2. multiprocessing_context: 'spawn' is more reliable in containers
# 3. num_idle_processes: Keep minimal to reduce memory usage
# 4. shutdown_process_timeout: Allow graceful shutdown
server = AgentServer(
    initialize_process_timeout=180.0,  # 3 minutes (default: 10s) - critical for cold start!
    shutdown_process_timeout=30.0,     # Graceful shutdown timeout
    multiprocessing_context="spawn",   # Better for containers (default: forkserver on Linux)
    num_idle_processes=1,              # Keep only 1 warm process (default: CPU count)
)


def prewarm(proc: JobProcess):
    """
    Prewarm function - called once when process starts.
    Pre-loads ML models to avoid timeout during first job.

    This is CRITICAL for Cloud Run deployment where cold start
    + model loading can exceed initialization timeout.
    """
    logger.info("🔥 Prewarming: Loading Silero VAD model...")
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("✅ Prewarm complete: VAD model loaded and cached")


# Register prewarm function - runs before any jobs are accepted
server.setup_fnc = prewarm


@server.rtc_session()
async def interview_agent(ctx: agents.JobContext):
    """Main agent entry point - runs for each interview session."""
    logger.info(f"Agent joining room: {ctx.room.name}")

    # ============================================
    # LAZY IMPORTS - Load heavy modules only when job starts
    # This avoids loading Google Gemini SDK etc. during subprocess spawn
    # ============================================
    from app.services.core.intelligence.prompt_manager import prompt_manager
    from app.services.core.intelligence.shadow_monitor import shadow_monitor
    from app.services.core.observability import (
        log_turn_event,
        evaluate_session_post_completion,
        observability_service,
    )
    from app.services.core.intelligence.candidate_profile import (
        candidate_profile_manager,
        CandidateProfile
    )
    from app.services.core.intelligence.scoring_engine import scoring_engine
    from app.services.core.intelligence.difficulty_adapter import (
        difficulty_adapter,
        DifficultyLevel,
        DifficultyState
    )
    from app.services.core.intelligence.competency_evaluator import competency_evaluator
    from app.services.core.intelligence.cross_stage_memory import cross_stage_memory
    logger.info("✅ Lazy imports loaded")

    # Fetch session details from database
    stage_type = "hr"
    job_role = "General"
    has_resume = False
    has_jd = False
    language = "en"  # Default language
    
    async with AsyncSessionLocal() as db:
        from sqlalchemy.orm import selectinload
        stmt = select(InterviewSession).options(
            selectinload(InterviewSession.application)
        ).where(
            InterviewSession.session_id == ctx.room.name
        )
        result = await db.execute(stmt)
        session_data = result.scalar_one_or_none()
        
        if session_data:
            stage_type = session_data.stage_type or "hr"
            job_role = session_data.job_role or "General"
            has_resume = bool(session_data.resume_text)
            has_jd = bool(session_data.job_description)
            language = session_data.language or "en"
            logger.info(f"Session found: stage_type={session_data.stage_type}, resolved_stage={stage_type}, language={language}")
        else:
            logger.warning(f"No session found for room: {ctx.room.name}, defaulting to HR")
    
    # Build agent configuration from centralized config
    context_info = ""
    if has_resume:
        context_info = "You have reviewed the candidate's resume."
    elif has_jd:
        context_info = "You have the job description but no resume. Ask about their background."
    else:
        context_info = f"You are interviewing for a {job_role} position."

    # Intelligence v2: Initialize candidate profile and cross-stage memory
    resume_text = session_data.resume_text if session_data else ""
    jd_text = session_data.job_description if session_data else ""
    application_id = session_data.application_id if session_data else None

    # Create initial candidate profile
    candidate_profile = await candidate_profile_manager.create_initial_profile(
        resume_text=resume_text,
        job_description=jd_text,
        session_id=ctx.room.name
    )
    logger.info(f"📊 Candidate profile initialized with {len(candidate_profile.verified_skills)} claimed skills")

    # Initialize difficulty state
    difficulty_state = difficulty_adapter.create_initial_state(
        starting_level=difficulty_adapter.get_level_for_stage(stage_type)
    )

    # Get cross-stage insights from previous stages
    previous_insights_context = ""
    if application_id and stage_type in ["technical", "behavioral"]:
        try:
            previous_insights = await cross_stage_memory.get_previous_insights(
                application_id=application_id,
                current_stage=stage_type
            )
            if previous_insights:
                previous_insights_context = cross_stage_memory.build_context_prompt(previous_insights)
                logger.info(f"📚 Loaded insights from {len(previous_insights)} previous stage(s)")
        except Exception as e:
            logger.warning(f"Failed to load cross-stage insights: {e}")

    # Get competency focus for this stage
    competency_focus = competency_evaluator.get_interview_guidance(
        stage_type=stage_type,
        job_role=job_role
    )

    # Track scores for this session
    turn_scores = []

    instructions = prompt_manager.get_system_instruction(
        stage_type=stage_type,
        job_role=job_role,
        context_info=context_info,
        language=language,
        resume_text=resume_text,
        job_description=jd_text,
        session_id=ctx.room.name,
        # Intelligence v2 parameters
        previous_stage_insights=previous_insights_context,
        candidate_profile_context=candidate_profile_manager.to_context_string(candidate_profile),
        difficulty_level=difficulty_state.level.value,
        competency_focus=competency_focus
    )
    voice_model = prompt_manager.get_voice_model(stage_type, language, session_id=ctx.room.name)
    
    # Map language to Google STT language code
    stt_language = "en-US" if language == "en" else "vi-VN"
    
    logger.info(f"🎙️ CONFIG: stage_type={stage_type}, language={language}, voice={voice_model}, stt_lang={stt_language}")
    
    try:
        logger.info(f"Initializing STT (Google Cloud: {stt_language})...")
        stt_plugin = google.STT(languages=stt_language, interim_results=False)
        
        logger.info(f"Initializing LLM (Google Gemini: {settings.GEMINI_MODEL})...")
        llm_plugin = google.LLM(model=settings.GEMINI_MODEL)
        
        # Initialize TTS (Cartesia)
        if language == "vi":
            cartesia_model = "sonic-3"
            logger.info(f"Using Cartesia Sonic 3.0 for Vietnamese (Voice: {voice_model})")
        else:
            cartesia_model = "sonic-english"
            logger.info(f"Using Cartesia Sonic English for English (Voice: {voice_model})")
            
        tts_plugin = cartesia.TTS(voice=voice_model, language=language, model=cartesia_model)


        
        # Use pre-loaded VAD from prewarm (avoids timeout on cold start)
        logger.info("Using pre-loaded VAD (Silero) from prewarm...")
        vad_plugin = ctx.proc.userdata["vad"]
        
        # Create agent session with AI components
        session = AgentSession(
            stt=stt_plugin,
            llm=llm_plugin,
            tts=tts_plugin,
            vad=vad_plugin,
        )
        logger.info("✅ AgentSession initialized successfully")
    except Exception as e:
        logger.exception(f"❌ CRITICAL ERROR initializing plugins: {e}")
        # Re-raise to ensure process fails if initialization fails
        raise
    
    # Initialize transcript manager
    transcript_mgr = TranscriptManager(ctx.room.name)
    await transcript_mgr.start_periodic_save(interval_seconds=30)

    # Initialize Opik session trace
    from app.services.core.observability.models import TraceMetadata
    from app.services.core.observability.decorators import _current_trace_id

    trace_metadata = TraceMetadata(
        session_id=ctx.room.name,
        stage_type=stage_type,
        job_role=job_role,
        language=language
    )
    session_trace_id = await observability_service.start_trace(
        name=f"interview_session_{ctx.room.name}",
        metadata=trace_metadata
    )
    # Register session → trace mapping (works across async tasks)
    if session_trace_id:
        observability_service.register_session_trace(ctx.room.name, session_trace_id)
        # Also set ContextVar for same-task calls (token not stored - can't reset across contexts)
        _current_trace_id.set(session_trace_id)
        # Set session ID in context for automatic trace lookup in spawned tasks
        from app.services.core.observability import set_current_session_id
        set_current_session_id(ctx.room.name)
        # Persist trace_id to database for frontend access
        try:
            async with AsyncSessionLocal() as db:
                from sqlalchemy import update
                await db.execute(
                    update(InterviewSession)
                    .where(InterviewSession.session_id == ctx.room.name)
                    .values(opik_trace_id=session_trace_id)
                )
                await db.commit()
                logger.info(f"📊 Opik trace_id saved to database: {session_trace_id}")
        except Exception as e:
            logger.error(f"Failed to save opik_trace_id: {e}")
    logger.info(f"📊 Opik trace started: {session_trace_id}")

    # Log system prompt content for observability
    if session_trace_id:
        await observability_service.log_llm_call(
            trace_id=session_trace_id,
            model="system_prompt",
            input_prompt=f"Stage: {stage_type}, Role: {job_role}, Language: {language}",
            output_response=instructions[:2000],  # Truncate for storage
            metadata={
                "component": "session_init",
                "prompt_type": "system_instruction",
                "has_resume": has_resume,
                "has_jd": has_jd,
                "prompt_length": len(instructions)
            }
        )
        logger.info(f"📝 System prompt logged ({len(instructions)} chars)")

    # Setup shutdown callback
    async def on_shutdown():
        await transcript_mgr.stop_and_save()

        # Intelligence v2: Compute final competency scores
        final_competencies = None
        if turn_scores:
            try:
                final_competencies = competency_evaluator.compute_competency_scores(
                    turn_scores=turn_scores,
                    job_role=job_role
                )
                logger.info(
                    f"📊 Competency scores computed: Role fit = {final_competencies['role_fit_score']:.0f}%"
                )
            except Exception as e:
                logger.error(f"Failed to compute competency scores: {e}")

        # Intelligence v2: Save cross-stage insights for next stage
        if application_id and conversation_history:
            try:
                await cross_stage_memory.save_stage_insights(
                    application_id=application_id,
                    stage_type=stage_type,
                    profile=candidate_profile,
                    transcript=conversation_history,
                    scores=turn_scores,
                    job_role=job_role
                )
                logger.info(f"📚 Cross-stage insights saved for {stage_type}")
            except Exception as e:
                logger.error(f"Failed to save cross-stage insights: {e}")

        # Intelligence v2: Persist session data to database
        try:
            async with AsyncSessionLocal() as db:
                from sqlalchemy import update
                await db.execute(
                    update(InterviewSession)
                    .where(InterviewSession.session_id == ctx.room.name)
                    .values(
                        candidate_profile=candidate_profile.to_dict(),
                        skill_assessments=turn_scores,
                        difficulty_level=difficulty_state.level.value,
                        competency_scores=final_competencies,
                        topics_covered=list(candidate_profile.topics_covered)
                    )
                )
                await db.commit()
                logger.info("📊 Intelligence v2 data persisted to database")
        except Exception as e:
            logger.error(f"Failed to persist intelligence data: {e}")

        # Run post-session evaluation
        if conversation_history:
            logger.info("📊 Running post-session GEval evaluation...")
            try:
                eval_result = await evaluate_session_post_completion(
                    session_id=ctx.room.name,
                    transcript=conversation_history,
                    metadata={
                        "stage_type": stage_type,
                        "job_role": job_role,
                        "language": language,
                        "competency_scores": final_competencies
                    }
                )
                if eval_result:
                    logger.info(f"📊 GEval complete: overall={eval_result.overall_score:.2f}")
            except Exception as e:
                logger.error(f"GEval evaluation failed: {e}")

        # End Opik trace
        if session_trace_id:
            await observability_service.end_trace(
                trace_id=session_trace_id,
                output={
                    "total_turns": len(conversation_history),
                    "competency_scores": final_competencies,
                    "difficulty_final": difficulty_state.level.value
                },
                metadata={"status": "completed"}
            )
            # Cleanup: unregister session from registry
            observability_service.unregister_session_trace(ctx.room.name)
            # Note: ContextVar.reset() skipped - shutdown runs in different async context
            # Session registry is our primary trace lookup mechanism
            logger.info(f"📊 Opik trace ended: {session_trace_id}")

    ctx.add_shutdown_callback(on_shutdown)
    
    
    # Shadow Monitor State
    conversation_history = []

    # Wrapper to run shadow analysis safely
    async def run_shadow_analysis():
        # Only run if we have enough context (e.g., 2+ turns)
        if len(conversation_history) < 2:
            return

        intervention = await shadow_monitor.analyze(
            conversation_history,
            job_role=job_role,
            stage_type=stage_type,
            session_id=ctx.room.name  # Pass for trace lookup
        )
        
        if intervention:
            logger.info(f"⚡ Injecting Runtime Directive: {intervention}")
            # Dynamically update the agent's instructions
            new_instructions = f"{instructions}\n\n[IMPORTANT RUNTIME UPDATE]: {intervention}"
            # For LiveKit Agents, we update the agent state if supported, or just the instruction attribute
            # Assuming 'session.agent' gives access to the running InterviewAssistant instance
            if hasattr(session, 'agent'):
                session.agent.instructions = new_instructions

    # Track last assistant message for scoring
    last_assistant_message = ""

    # Intelligence v2: Async scoring and profile update
    async def process_user_response(question: str, answer: str, turn_num: int, session_id: str):
        """Process user response with scoring and profile updates."""
        nonlocal candidate_profile, difficulty_state

        try:
            # Score the answer
            score_result = await scoring_engine.score_answer(
                question=question,
                answer=answer,
                stage_type=stage_type,
                job_role=job_role,
                context={"profile": candidate_profile.to_dict()},
                session_id=session_id
            )

            # Record the score
            turn_scores.append({
                "turn": turn_num,
                "score": score_result.overall,
                "dimension": score_result.dimension,
                "feedback": score_result.feedback
            })

            logger.info(
                f"📝 Turn {turn_num} scored: {score_result.overall:.0f}/100 "
                f"[{score_result.dimension}] - {score_result.feedback[:50]}..."
            )

            # Log score to observability
            await observability_service.record_metric(
                metric_name="answer_score",
                value=score_result.overall,
                trace_id=session_trace_id,
                metadata={
                    "turn": turn_num,
                    "dimension": score_result.dimension,
                    "difficulty": difficulty_state.level.value
                }
            )

            # Update candidate profile
            candidate_profile = await candidate_profile_manager.update_after_turn(
                profile=candidate_profile,
                question=question,
                answer=answer,
                score=score_result.overall,
                session_id=session_id
            )

            # Update difficulty based on score
            difficulty_state = difficulty_adapter.update(
                state=difficulty_state,
                new_score=score_result.overall,
                current_turn=turn_num
            )

        except Exception as e:
            logger.error(f"Error in scoring/profile update: {e}")

    # Register transcript capture events BEFORE starting session
    @session.on("conversation_item_added")
    def on_conversation_item_added(event: ConversationItemAddedEvent):
        nonlocal last_assistant_message

        try:
            role = event.item.role
            text = event.item.text_content or ""
            transcript_mgr.add_message(role, text)

            # Shadow Monitor: Update History
            # Map LiveKit ChatRole to string
            role_str = "user" if role == agents.llm.ChatRole.USER else "assistant"
            conversation_history.append({"role": role_str, "content": text})

            # Track assistant messages for scoring context
            if role == agents.llm.ChatRole.ASSISTANT:
                last_assistant_message = text

            # Log turn event to Opik
            asyncio.create_task(log_turn_event(
                turn_index=len(conversation_history),
                role=role_str,
                content=text
            ))

            # Trigger analysis and scoring ONLY after USER turns
            if role == agents.llm.ChatRole.USER:
                asyncio.create_task(run_shadow_analysis())

                # Intelligence v2: Score the response and update profile
                if last_assistant_message and len(text.strip()) > 20:
                    asyncio.create_task(process_user_response(
                        question=last_assistant_message,
                        answer=text,
                        turn_num=len(conversation_history),
                        session_id=ctx.room.name
                    ))

        except Exception as e:
            logger.error(f"Error capturing transcript item: {e}")
    
    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event: UserInputTranscribedEvent):
        if event.is_final:
            logger.debug(f"User speech transcribed: {event.transcript}")
    
    @ctx.room.on("participant_disconnected")
    def on_participant_disconnect(participant):
        logger.info(f"Participant {participant.identity} disconnected.")
        asyncio.create_task(transcript_mgr.stop_and_save())
    
    # Start session AFTER event handlers are registered
    await session.start(
        room=ctx.room,
        agent=InterviewAssistant(instructions=instructions),
    )
    
    # Send initial greeting (now captured by event handler above)
    logger.info(f"Agent session started for {stage_type} round. Generating greeting...")
    initial_greeting = prompt_manager.get_greeting(stage_type, job_role, language, session_id=ctx.room.name)
    await session.generate_reply(instructions=initial_greeting)
    logger.info("Initial greeting sent")


if __name__ == "__main__":
    agents.cli.run_app(server)
