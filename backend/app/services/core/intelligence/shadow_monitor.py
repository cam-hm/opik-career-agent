import os
import json
import logging
import time
from typing import List, Dict, Optional
from google import genai
from jinja2 import Template
from app.services.core.intelligence.prompt_manager import prompt_manager
from config.settings import get_settings

logger = logging.getLogger("shadow-monitor")

class ShadowMonitor:
    """
    Background intelligence that monitors the interview loop.
    Uses a fast/cheap LLM (Gemini Flash) to analyze state and intervene.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.model_name = self.settings.SHADOW_MODEL
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found. Shadow Monitor disabled.")
            self.enabled = False
        else:
            self.client = genai.Client(api_key=self.api_key)
            self.enabled = True
            
        # Load template
        template_path = os.path.join(prompt_manager.templates_dir, "shadow_analysis.j2")
        with open(template_path, "r") as f:
            self.template = Template(f.read())
            
    async def analyze(
        self,
        transcript_history: List[Dict[str, str]],
        job_role: str,
        stage_type: str,
        session_id: str = None
    ) -> Optional[str]:
        """
        Analyze transcript and return an intervention directive if needed.
        Returns None if everything is flowing well.

        Args:
            session_id: Session ID for trace lookup (recommended for proper trace nesting)
        """
        if not self.enabled or len(transcript_history) < 2:
            return None

        # Format transcript for prompt
        # take last 6 messages for context
        recent = transcript_history[-6:]
        transcript_text = "\n".join([f"{m['role']}: {m['content']}" for m in recent])
        
        prompt = self.template.render(
            transcript=transcript_text,
            job_role=job_role,
            stage_type=stage_type
        )
        
        try:
            # Import observability (lazy to avoid circular imports)
            from app.services.core.observability import observability_service, get_current_trace_id

            # Get trace_id: prefer session lookup (works across async tasks), fallback to context
            trace_id = None
            if session_id:
                trace_id = observability_service.get_trace_for_session(session_id)
            if not trace_id:
                trace_id = get_current_trace_id()

            start_time = time.time()

            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )

            latency_ms = (time.time() - start_time) * 1000

            result = json.loads(response.text)
            status = result.get("status", "flowing")
            intervention = result.get("intervention")

            # Log to Opik (provider handles truncation, send full data)
            await observability_service.log_llm_call(
                trace_id=trace_id,
                model=self.model_name,
                input_prompt=prompt,  # Full prompt, provider truncates if needed
                output_response=response.text,  # Full response
                metadata={
                    "component": "shadow_monitor",
                    "status": status,
                    "has_intervention": bool(intervention),
                    "prompt_length": len(prompt),
                    "response_length": len(response.text)
                },
                latency_ms=latency_ms
            )

            if status != "flowing" and intervention:
                logger.info(f"🦇 Shadow Monitor Intervention ({status}): {intervention}")

                # Log intervention as metric for tracking
                await observability_service.record_metric(
                    metric_name="shadow_intervention",
                    value=1.0,  # Binary: intervention triggered
                    trace_id=trace_id,
                    metadata={
                        "status": status,
                        "intervention_text": intervention[:200],
                        "turn_count": len(transcript_history)
                    }
                )
                return intervention

            return None

        except Exception as e:
            logger.error(f"Shadow Monitor Analysis Failed: {e}")
            return None
            
# Singleton for easy import
shadow_monitor = ShadowMonitor()
