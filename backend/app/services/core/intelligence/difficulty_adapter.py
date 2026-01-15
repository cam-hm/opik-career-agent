"""
Adaptive Difficulty Controller.

Dynamically adjusts interview difficulty based on candidate performance.
Implements hysteresis to prevent rapid oscillation between levels.
"""
import logging
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("difficulty-adapter")


class DifficultyLevel(Enum):
    """Interview difficulty levels."""
    FOUNDATIONAL = "foundational"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

    @property
    def description(self) -> str:
        """Get human-readable description."""
        descriptions = {
            "foundational": "Basic concepts and fundamentals",
            "intermediate": "Applied knowledge and common scenarios",
            "advanced": "Complex scenarios and edge cases",
            "expert": "Industry-leading, architectural decisions"
        }
        return descriptions.get(self.value, "Unknown")

    @property
    def question_guidance(self) -> str:
        """Get guidance for question generation at this level."""
        guidance = {
            "foundational": "Ask about basic concepts, definitions, and simple use cases. Single-step problems.",
            "intermediate": "Ask about common patterns, standard implementations, and typical scenarios. Multi-step problems.",
            "advanced": "Ask about edge cases, optimization, trade-offs, and complex integrations. Requires analysis.",
            "expert": "Ask about architectural decisions, innovation, and strategic thinking. Open-ended design problems."
        }
        return guidance.get(self.value, "")


@dataclass
class DifficultyState:
    """Current difficulty state with metadata."""
    level: DifficultyLevel
    turns_at_level: int
    last_change_turn: int
    change_reason: Optional[str]
    score_window: List[float]  # Recent scores for decision making

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "level": self.level.value,
            "turns_at_level": self.turns_at_level,
            "last_change_turn": self.last_change_turn,
            "change_reason": self.change_reason,
            "score_window": self.score_window
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DifficultyState":
        """Create from dictionary."""
        if not data:
            return cls(
                level=DifficultyLevel.INTERMEDIATE,
                turns_at_level=0,
                last_change_turn=0,
                change_reason=None,
                score_window=[]
            )
        return cls(
            level=DifficultyLevel(data.get("level", "intermediate")),
            turns_at_level=data.get("turns_at_level", 0),
            last_change_turn=data.get("last_change_turn", 0),
            change_reason=data.get("change_reason"),
            score_window=data.get("score_window", [])
        )


class DifficultyAdapter:
    """
    Adapts interview difficulty based on candidate performance.

    Uses a sliding window of recent scores to make decisions,
    with hysteresis to prevent rapid oscillation.
    """

    def __init__(
        self,
        increase_threshold: float = 80.0,
        decrease_threshold: float = 50.0,
        min_turns_at_level: int = 2,
        window_size: int = 3
    ):
        """
        Initialize the difficulty adapter.

        Args:
            increase_threshold: Average score above this triggers increase
            decrease_threshold: Average score below this triggers decrease
            min_turns_at_level: Minimum turns before changing (hysteresis)
            window_size: Number of recent scores to consider
        """
        self.increase_threshold = increase_threshold
        self.decrease_threshold = decrease_threshold
        self.min_turns_at_level = min_turns_at_level
        self.window_size = window_size

        # Level ordering for navigation
        self.levels = list(DifficultyLevel)

    def create_initial_state(
        self,
        starting_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    ) -> DifficultyState:
        """Create initial difficulty state."""
        return DifficultyState(
            level=starting_level,
            turns_at_level=0,
            last_change_turn=0,
            change_reason="Initial level",
            score_window=[]
        )

    def update(
        self,
        state: DifficultyState,
        new_score: float,
        current_turn: int
    ) -> DifficultyState:
        """
        Update difficulty state based on new score.

        Args:
            state: Current difficulty state
            new_score: Score from the latest answer (0-100)
            current_turn: Current turn number

        Returns:
            Updated DifficultyState (may have changed level)
        """
        # Add score to window
        state.score_window.append(new_score)
        if len(state.score_window) > self.window_size:
            state.score_window = state.score_window[-self.window_size:]

        state.turns_at_level += 1

        # Not enough data to make a decision
        if len(state.score_window) < 2:
            return state

        # Check if we've been at this level long enough
        if state.turns_at_level < self.min_turns_at_level:
            return state

        # Calculate metrics
        avg_score = sum(state.score_window) / len(state.score_window)
        trend = state.score_window[-1] - state.score_window[0]

        # Decision logic
        new_level = state.level
        reason = None

        if avg_score >= self.increase_threshold and trend >= 0:
            # Candidate is doing very well, increase difficulty
            new_level = self._increase_level(state.level)
            if new_level != state.level:
                reason = f"High performance (avg: {avg_score:.1f}, trend: +{trend:.1f})"

        elif avg_score <= self.decrease_threshold and trend <= 0:
            # Candidate is struggling, decrease difficulty
            new_level = self._decrease_level(state.level)
            if new_level != state.level:
                reason = f"Struggling (avg: {avg_score:.1f}, trend: {trend:.1f})"

        # Apply level change if needed
        if new_level != state.level:
            logger.info(
                f"Difficulty change: {state.level.value} -> {new_level.value} "
                f"(reason: {reason})"
            )
            return DifficultyState(
                level=new_level,
                turns_at_level=0,
                last_change_turn=current_turn,
                change_reason=reason,
                score_window=state.score_window  # Keep window for continuity
            )

        return state

    def _increase_level(self, current: DifficultyLevel) -> DifficultyLevel:
        """Move to next higher difficulty level."""
        current_idx = self.levels.index(current)
        new_idx = min(current_idx + 1, len(self.levels) - 1)
        return self.levels[new_idx]

    def _decrease_level(self, current: DifficultyLevel) -> DifficultyLevel:
        """Move to next lower difficulty level."""
        current_idx = self.levels.index(current)
        new_idx = max(current_idx - 1, 0)
        return self.levels[new_idx]

    def get_level_for_stage(self, stage_type: str) -> DifficultyLevel:
        """Get recommended starting difficulty for a stage type."""
        # HR is generally easier, technical starts at intermediate
        stage_defaults = {
            "hr": DifficultyLevel.INTERMEDIATE,
            "technical": DifficultyLevel.INTERMEDIATE,
            "behavioral": DifficultyLevel.INTERMEDIATE,
            "practice": DifficultyLevel.FOUNDATIONAL
        }
        return stage_defaults.get(stage_type, DifficultyLevel.INTERMEDIATE)

    def get_prompt_injection(self, state: DifficultyState) -> str:
        """
        Get prompt text to inject based on current difficulty.

        Returns a string to add to the system prompt that guides
        question difficulty.
        """
        level = state.level

        return f"""
CURRENT DIFFICULTY LEVEL: {level.value.upper()}

{level.question_guidance}

Recent performance: {self._describe_performance(state)}
"""

    def _describe_performance(self, state: DifficultyState) -> str:
        """Describe recent performance for context."""
        if not state.score_window:
            return "No data yet"

        avg = sum(state.score_window) / len(state.score_window)
        if avg >= 80:
            return f"Excellent ({avg:.0f}/100 avg)"
        elif avg >= 60:
            return f"Good ({avg:.0f}/100 avg)"
        elif avg >= 40:
            return f"Fair ({avg:.0f}/100 avg)"
        else:
            return f"Struggling ({avg:.0f}/100 avg)"

    def should_provide_hints(self, state: DifficultyState) -> bool:
        """Determine if hints should be provided based on difficulty."""
        # Provide hints at lower difficulty levels or when struggling
        if state.level in [DifficultyLevel.FOUNDATIONAL]:
            return True
        if state.score_window and sum(state.score_window) / len(state.score_window) < 40:
            return True
        return False


# Singleton instance
difficulty_adapter = DifficultyAdapter()
