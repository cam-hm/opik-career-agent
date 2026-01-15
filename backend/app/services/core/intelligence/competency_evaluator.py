"""
Competency Evaluator.

Maps interview scores to competency frameworks.
Computes role-weighted final scores and rubric-based assessments.
"""
import yaml
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path
from config.settings import get_settings

logger = logging.getLogger("competency-evaluator")


@dataclass
class CompetencyScore:
    """Score for a single competency."""
    competency: str
    score: float  # 0-100
    rubric_level: str  # Human-readable level description
    evidence: List[str]  # Turn references showing this competency
    sample_size: int  # Number of data points


class CompetencyEvaluator:
    """
    Evaluates candidate performance against a competency framework.

    Loads competency definitions from YAML config and maps
    per-turn dimension scores to competency scores.
    """

    def __init__(self):
        self.settings = get_settings()
        self._load_config()

    def _load_config(self):
        """Load competency configuration from YAML."""
        config_path = self.settings.base_path / "config" / "competencies.yaml"
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
                logger.info("Competency config loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load competency config: {e}")
            # Fallback to minimal config
            self.config = {
                "competencies": {},
                "role_competency_weights": {"default": {}},
                "stage_competency_focus": {},
                "dimension_competency_map": {}
            }

    def map_dimension_to_competency(self, dimension: str) -> str:
        """
        Map a scoring dimension to its parent competency.

        Args:
            dimension: Dimension name (e.g., "system_design", "clarity")

        Returns:
            Competency name (e.g., "technical_depth", "communication")
        """
        dimension_map = self.config.get("dimension_competency_map", {})
        return dimension_map.get(dimension, "general")

    def get_role_weights(self, job_role: str) -> Dict[str, float]:
        """
        Get competency weights for a specific role.

        Args:
            job_role: The target job role

        Returns:
            Dictionary of competency -> weight
        """
        weights = self.config.get("role_competency_weights", {})

        # Try exact match first
        if job_role in weights:
            return weights[job_role]

        # Try fuzzy match (role contains keyword)
        job_lower = job_role.lower()
        for role, w in weights.items():
            if role.lower() in job_lower or job_lower in role.lower():
                return w

        # Fallback to default
        return weights.get("default", {
            "technical_depth": 0.35,
            "communication": 0.20,
            "problem_solving": 0.30,
            "leadership": 0.15
        })

    def get_stage_focus(self, stage_type: str) -> List[str]:
        """
        Get competencies to focus on for this interview stage.

        Args:
            stage_type: Interview stage (hr, technical, behavioral)

        Returns:
            List of competency names to prioritize
        """
        focus_map = self.config.get("stage_competency_focus", {})
        return focus_map.get(stage_type, ["technical_depth", "communication"])

    def get_rubric_level(self, competency: str, score: float) -> str:
        """
        Get the rubric level description for a score.

        Args:
            competency: Competency name
            score: Score (0-100)

        Returns:
            Human-readable rubric level description
        """
        competencies = self.config.get("competencies", {})
        comp_config = competencies.get(competency, {})
        rubric = comp_config.get("rubric", {})

        for range_str, level in rubric.items():
            try:
                low, high = map(int, range_str.split("-"))
                if low <= score <= high:
                    return level
            except ValueError:
                continue

        # Default descriptions
        if score >= 85:
            return "Exceptional - Top performer"
        elif score >= 70:
            return "Strong - Above expectations"
        elif score >= 50:
            return "Adequate - Meets expectations"
        else:
            return "Needs Development - Below expectations"

    def compute_competency_scores(
        self,
        turn_scores: List[Dict[str, Any]],
        job_role: str
    ) -> Dict[str, Any]:
        """
        Compute final competency scores from per-turn assessment data.

        Args:
            turn_scores: List of per-turn scores with dimensions
                [{"turn": 1, "score": 75, "dimension": "system_design"}, ...]
            job_role: Target job role for weight calculation

        Returns:
            Comprehensive competency evaluation
        """
        if not turn_scores:
            return {
                "competency_scores": {},
                "role_fit_score": 0,
                "role_weights_used": {},
                "summary": "No scoring data available"
            }

        # Group scores by competency
        competency_scores: Dict[str, List[float]] = defaultdict(list)
        competency_evidence: Dict[str, List[str]] = defaultdict(list)

        for turn in turn_scores:
            dimension = turn.get("dimension", "general")
            score = turn.get("score", 50)
            turn_num = turn.get("turn", 0)

            competency = self.map_dimension_to_competency(dimension)
            competency_scores[competency].append(score)
            competency_evidence[competency].append(f"Turn {turn_num}")

        # Compute per-competency results
        results: Dict[str, CompetencyScore] = {}
        for comp, scores in competency_scores.items():
            avg_score = sum(scores) / len(scores)
            results[comp] = CompetencyScore(
                competency=comp,
                score=round(avg_score, 1),
                rubric_level=self.get_rubric_level(comp, avg_score),
                evidence=competency_evidence[comp][:5],  # Limit evidence
                sample_size=len(scores)
            )

        # Compute role fit score (weighted average)
        weights = self.get_role_weights(job_role)
        role_fit = 0.0
        weight_sum = 0.0

        for comp, weight in weights.items():
            if comp in results:
                role_fit += results[comp].score * weight
                weight_sum += weight
            else:
                # If competency not measured, use neutral score
                role_fit += 50.0 * weight
                weight_sum += weight

        role_fit_score = role_fit / weight_sum if weight_sum > 0 else 50.0

        # Generate summary
        summary = self._generate_summary(results, role_fit_score, job_role)

        return {
            "competency_scores": {
                comp: {
                    "score": cs.score,
                    "rubric_level": cs.rubric_level,
                    "sample_size": cs.sample_size,
                    "evidence": cs.evidence
                }
                for comp, cs in results.items()
            },
            "role_fit_score": round(role_fit_score, 1),
            "role_weights_used": weights,
            "summary": summary
        }

    def _generate_summary(
        self,
        results: Dict[str, CompetencyScore],
        role_fit: float,
        job_role: str
    ) -> str:
        """Generate a brief summary of the competency evaluation."""
        if not results:
            return "Insufficient data for evaluation"

        # Find strengths (above 70)
        strengths = [
            cs.competency for cs in results.values()
            if cs.score >= 70
        ]

        # Find areas for development (below 50)
        development = [
            cs.competency for cs in results.values()
            if cs.score < 50
        ]

        parts = []

        if role_fit >= 75:
            parts.append(f"Strong fit for {job_role} role ({role_fit:.0f}%)")
        elif role_fit >= 60:
            parts.append(f"Moderate fit for {job_role} role ({role_fit:.0f}%)")
        else:
            parts.append(f"Below target for {job_role} role ({role_fit:.0f}%)")

        if strengths:
            parts.append(f"Strengths: {', '.join(strengths)}")

        if development:
            parts.append(f"Development areas: {', '.join(development)}")

        return ". ".join(parts) + "."

    def get_competency_details(self, competency: str) -> Dict[str, Any]:
        """
        Get detailed information about a competency.

        Args:
            competency: Competency name

        Returns:
            Competency definition with dimensions and rubric
        """
        competencies = self.config.get("competencies", {})
        return competencies.get(competency, {
            "name": competency.title(),
            "description": "No description available",
            "dimensions": [],
            "rubric": {}
        })

    def get_interview_guidance(
        self,
        stage_type: str,
        job_role: str,
        current_scores: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Get guidance for the interviewer based on competency focus.

        Args:
            stage_type: Interview stage
            job_role: Target job role
            current_scores: Optional current competency scores

        Returns:
            Guidance text for system prompt injection
        """
        focus_competencies = self.get_stage_focus(stage_type)
        weights = self.get_role_weights(job_role)

        # Get competency descriptions
        guidance_parts = [
            f"COMPETENCY FOCUS for {stage_type.upper()} stage:"
        ]

        for comp in focus_competencies:
            details = self.get_competency_details(comp)
            weight = weights.get(comp, 0)
            guidance_parts.append(
                f"- {details.get('name', comp)} (weight: {weight*100:.0f}%): "
                f"{details.get('description', '')}"
            )

        # Add gaps to probe if we have current scores
        if current_scores:
            low_comps = [
                comp for comp, score in current_scores.items()
                if score < 50 and comp in focus_competencies
            ]
            if low_comps:
                guidance_parts.append(
                    f"\nPRIORITY: Probe deeper on {', '.join(low_comps)} (currently weak)"
                )

        return "\n".join(guidance_parts)


# Singleton instance
competency_evaluator = CompetencyEvaluator()
