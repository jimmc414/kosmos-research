"""
Plan Reviewer Agent for Kosmos.

This implements the karpathy Plan Reviewer pattern for validating
research plans before execution.

Pattern source: R&D/kosmos-karpathy
Gap addressed: Gap 2 (Task Generation Strategy)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import yaml

from kosmos.core.llm import get_client

logger = logging.getLogger(__name__)


class PlanReviewerAgent:
    """
    Reviews and validates research plans.

    This agent scores plans on 5 dimensions (specificity, relevance,
    novelty, coverage, feasibility) and provides feedback for improvement.
    """

    def __init__(self, min_average_score: float = 7.0):
        """
        Initialize plan reviewer.

        Args:
            min_average_score: Minimum average score for approval (0-10)
        """
        self.client = get_client()
        self.min_average_score = min_average_score

        # Load instructions
        instructions_path = Path(__file__).parent / "instructions.yaml"
        with open(instructions_path) as f:
            instructions = yaml.safe_load(f)
            self.instruction = instructions["plan_reviewer"]

    async def review_plan(
        self,
        plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Review and validate a research plan.

        Args:
            plan: Plan from Plan Creator with tasks list
            context: Current state for validation

        Returns:
            Dict with:
                - approved: bool
                - scores: Dict of dimension scores
                - average_score: float
                - feedback: str
                - suggestions: List[str]
                - required_changes: List[str]
        """
        logger.info(f"Reviewing plan with {len(plan.get('tasks', []))} tasks")

        # Build review prompt
        prompt = self._build_review_prompt(plan, context)

        # Query LLM for review
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=messages,
                temperature=0.3  # Lower temperature for consistent evaluation
            )

            # Parse review
            review = self._parse_review(response.content[0].text)

            # Validate review structure
            review = self._validate_review(review, plan)

            logger.info(
                f"Plan review complete: "
                f"{'APPROVED' if review['approved'] else 'REJECTED'} "
                f"(avg score: {review['average_score']:.1f}/10)"
            )

            return review

        except Exception as e:
            logger.error(f"Plan review failed: {e}")
            # Return conservative default review
            return self._default_review(plan, approved=False)

    def _build_review_prompt(
        self,
        plan: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Build the review prompt."""
        prompt = f"{self.instruction}\n\n"
        prompt += "=" * 80 + "\n"
        prompt += "PLAN TO REVIEW\n"
        prompt += "=" * 80 + "\n\n"

        # Plan rationale
        if "rationale" in plan:
            prompt += f"**Plan Rationale**: {plan['rationale']}\n\n"

        # Tasks
        tasks = plan.get("tasks", [])
        prompt += f"**Number of Tasks**: {len(tasks)}\n\n"

        if tasks:
            prompt += "**Tasks**:\n\n"
            for task in tasks:
                prompt += f"Task {task.get('id', '?')}:\n"
                prompt += f"  Type: {task.get('type', 'unknown')}\n"
                prompt += f"  Description: {task.get('description', 'No description')}\n"
                prompt += f"  Expected Output: {task.get('expected_output', 'None')}\n"
                if task.get('target_hypotheses'):
                    prompt += f"  Target Hypotheses: {task.get('target_hypotheses')}\n"
                if task.get('required_skills'):
                    prompt += f"  Required Skills: {', '.join(task.get('required_skills', []))}\n"
                prompt += f"  Estimated Time: {task.get('estimated_time_minutes', '?')} minutes\n"
                prompt += f"  Exploration: {task.get('exploration', True)}\n"
                prompt += "\n"

        # Context for review
        prompt += "**Context for Review**:\n\n"
        prompt += f"- Current Cycle: {context.get('cycle', '?')}/20\n"
        prompt += f"- Total Findings: {context.get('findings_count', 0)}\n"
        prompt += f"- Unsupported Hypotheses: {len(context.get('unsupported_hypotheses', []))}\n"
        prompt += f"- Past Tasks: {len(context.get('past_tasks', []))}\n\n"

        # Past tasks for novelty check
        past_tasks = context.get('past_tasks', [])
        if past_tasks:
            prompt += "**Recent Past Tasks** (for novelty check):\n"
            for i, task in enumerate(past_tasks[-10:], 1):
                prompt += f"{i}. [{task.get('type')}] {task.get('description', 'No desc')}\n"
            prompt += "\n"

        prompt += "=" * 80 + "\n"
        prompt += "REVIEW THE PLAN\n"
        prompt += "=" * 80 + "\n\n"

        prompt += "Score each dimension 0-10 according to the criteria above.\n"
        prompt += "Provide specific, actionable feedback.\n"
        prompt += "Output your review as valid JSON matching the format in the instructions.\n"

        return prompt

    def _parse_review(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM review response."""
        # Extract JSON
        if "```json" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_text = response_text

        try:
            review = json.loads(json_text)
            return review
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse review JSON: {e}")
            raise ValueError(f"Could not parse review: {response_text[:500]}")

    def _validate_review(
        self,
        review: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and normalize review structure."""
        # Ensure scores exist
        if "scores" not in review:
            review["scores"] = {}

        required_dimensions = ["specificity", "relevance", "novelty", "coverage", "feasibility"]
        for dim in required_dimensions:
            if dim not in review["scores"]:
                logger.warning(f"Missing score for {dim}, defaulting to 5.0")
                review["scores"][dim] = 5.0

        # Calculate average
        scores = review["scores"]
        avg = sum(scores[dim] for dim in required_dimensions) / len(required_dimensions)
        review["average_score"] = round(avg, 1)

        # Determine approval
        min_score = min(scores.values())
        approved = (
            avg >= self.min_average_score and
            min_score >= 5.0 and
            self._check_task_requirements(plan)
        )

        review["approved"] = approved

        # Ensure feedback exists
        if "feedback" not in review:
            if approved:
                review["feedback"] = f"Plan approved with average score {avg:.1f}/10"
            else:
                review["feedback"] = f"Plan needs improvement (average score {avg:.1f}/10)"

        # Ensure suggestions/changes exist
        if "suggestions" not in review:
            review["suggestions"] = []
        if "required_changes" not in review:
            review["required_changes"] = []

        return review

    def _check_task_requirements(self, plan: Dict[str, Any]) -> bool:
        """Check minimum task requirements."""
        tasks = plan.get("tasks", [])

        if len(tasks) < 5:
            logger.warning(f"Too few tasks: {len(tasks)} < 5")
            return False

        # Count task types
        task_types = [t.get("type") for t in tasks]
        data_analysis_count = task_types.count("data_analysis")

        if data_analysis_count < 3:
            logger.warning(f"Too few data_analysis tasks: {data_analysis_count} < 3")
            return False

        # Check type diversity
        unique_types = set(task_types)
        if len(unique_types) < 2:
            logger.warning(f"Insufficient task type diversity: {unique_types}")
            return False

        return True

    def _default_review(
        self,
        plan: Dict[str, Any],
        approved: bool
    ) -> Dict[str, Any]:
        """Generate default review when LLM fails."""
        return {
            "approved": approved,
            "scores": {
                "specificity": 5.0,
                "relevance": 5.0,
                "novelty": 5.0,
                "coverage": 5.0,
                "feasibility": 5.0
            },
            "average_score": 5.0,
            "feedback": "Default review (LLM evaluation failed). Manual review recommended.",
            "suggestions": ["Review plan manually"],
            "required_changes": [] if approved else ["LLM evaluation failed, revise manually"]
        }

    def quick_validate(self, plan: Dict[str, Any]) -> bool:
        """
        Quick validation without LLM.

        Checks basic structure and requirements.
        Useful for fast pre-checks.

        Args:
            plan: Plan to validate

        Returns:
            True if passes basic checks
        """
        # Check structure
        if not isinstance(plan, dict):
            return False

        if "tasks" not in plan:
            return False

        tasks = plan["tasks"]
        if not isinstance(tasks, list):
            return False

        # Check task count
        if len(tasks) < 5 or len(tasks) > 15:
            return False

        # Check each task has required fields
        required_fields = ["id", "type", "description"]
        for task in tasks:
            if not all(field in task for field in required_fields):
                return False

        # Check task type requirements
        if not self._check_task_requirements(plan):
            return False

        return True
