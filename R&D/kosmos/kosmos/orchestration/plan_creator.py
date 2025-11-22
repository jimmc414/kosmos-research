"""
Plan Creator Agent for Kosmos.

This implements the karpathy Plan Creator pattern for generating
strategic research plans with 10 prioritized tasks per cycle.

Pattern source: R&D/kosmos-karpathy
Gap addressed: Gap 2 (Task Generation Strategy)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml

from kosmos.core.llm import get_client
from kosmos.agents.skill_loader import SkillLoader

logger = logging.getLogger(__name__)


class PlanCreatorAgent:
    """
    Creates strategic research plans for discovery cycles.

    This agent analyzes the current state of research and generates
    10 specific, actionable tasks that advance the research objective.
    """

    def __init__(self):
        """Initialize plan creator."""
        self.client = get_client()
        self.skill_loader = SkillLoader()

        # Load instructions
        instructions_path = Path(__file__).parent / "instructions.yaml"
        with open(instructions_path) as f:
            instructions = yaml.safe_load(f)
            self.instruction = instructions["plan_creator"]
            self.common_instruction = instructions["common_instructions"]

    async def create_plan(
        self,
        research_objective: str,
        context: Dict[str, Any],
        num_tasks: int = 10
    ) -> Dict[str, Any]:
        """
        Generate research plan with N tasks.

        Args:
            research_objective: The overarching scientific question
            context: Current state including:
                - cycle: Current cycle number
                - findings_count: Number of findings so far
                - recent_findings: Last few findings
                - unsupported_hypotheses: Hypotheses needing validation
                - past_tasks: Previously completed tasks
                - exploration_ratio: 0.0-1.0, exploration vs exploitation
            num_tasks: Number of tasks to generate (default: 10)

        Returns:
            Dict with:
                - tasks: List of task dicts
                - rationale: Strategic reasoning
                - metadata: Additional info
        """
        logger.info(f"Creating plan for cycle {context.get('cycle', 'unknown')}")

        # Build prompt
        prompt = self._build_prompt(research_objective, context, num_tasks)

        # Query LLM
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=messages,
                temperature=0.7  # Some creativity for task generation
            )

            # Parse response
            plan = self._parse_response(response.content[0].text)

            # Validate plan structure
            plan = self._validate_plan(plan, num_tasks)

            logger.info(f"Generated plan with {len(plan['tasks'])} tasks")

            return plan

        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            # Return fallback plan
            return self._fallback_plan(research_objective, context, num_tasks)

    def _build_prompt(
        self,
        research_objective: str,
        context: Dict[str, Any],
        num_tasks: int
    ) -> str:
        """Build the prompt for plan creation."""
        exploration_ratio = context.get('exploration_ratio', 0.5)
        cycle = context.get('cycle', 1)

        prompt = f"{self.instruction}\n\n{self.common_instruction}\n\n"
        prompt += "=" * 80 + "\n"
        prompt += "CURRENT RESEARCH CONTEXT\n"
        prompt += "=" * 80 + "\n\n"

        prompt += f"**Research Objective**: {research_objective}\n\n"
        prompt += f"**Current Cycle**: {cycle}/20\n\n"
        prompt += f"**Exploration Ratio**: {exploration_ratio:.1%} (exploration) / {(1-exploration_ratio):.1%} (exploitation)\n\n"

        # Findings summary
        findings_count = context.get('findings_count', 0)
        prompt += f"**Total Findings So Far**: {findings_count}\n\n"

        recent_findings = context.get('recent_findings', [])
        if recent_findings:
            prompt += "**Recent Findings** (last 3):\n"
            for i, finding in enumerate(recent_findings[-3:], 1):
                prompt += f"{i}. {finding.get('summary', 'No summary')}\n"
            prompt += "\n"

        # Hypotheses needing validation
        unsupported = context.get('unsupported_hypotheses', [])
        if unsupported:
            prompt += f"**Unsupported Hypotheses** ({len(unsupported)} need validation):\n"
            for i, hyp in enumerate(unsupported[:5], 1):  # Show top 5
                prompt += f"{i}. {hyp.get('text', 'Unknown')}\n"
            prompt += "\n"

        # Past tasks (for novelty checking)
        past_tasks = context.get('past_tasks', [])
        if past_tasks:
            prompt += f"**Previously Completed Tasks** ({len(past_tasks)} total, showing recent):\n"
            for i, task in enumerate(past_tasks[-10:], 1):  # Show last 10
                prompt += f"{i}. [{task.get('type', 'unknown')}] {task.get('description', 'No description')}\n"
            prompt += "\n"

        # Available skills
        prompt += "**Available Scientific Skills**:\n"
        available_skills = self.skill_loader.get_available_skills()
        prompt += f"You have access to {len(available_skills)} specialized skills including: "
        prompt += ", ".join(available_skills[:20])  # Show first 20
        if len(available_skills) > 20:
            prompt += f", and {len(available_skills) - 20} more...\n\n"
        else:
            prompt += "\n\n"

        # Task generation request
        prompt += "=" * 80 + "\n"
        prompt += f"GENERATE {num_tasks} TASKS FOR THIS CYCLE\n"
        prompt += "=" * 80 + "\n\n"

        prompt += f"Create {num_tasks} specific, actionable research tasks following the guidelines above.\n\n"

        prompt += "Remember:\n"
        if exploration_ratio > 0.6:
            prompt += "- HIGH EXPLORATION: Focus on discovering new directions\n"
        elif exploration_ratio < 0.4:
            prompt += "- HIGH EXPLOITATION: Focus on validating and deepening existing findings\n"
        else:
            prompt += "- BALANCED: Mix exploration of new areas with validation of existing findings\n"

        prompt += "- Be SPECIFIC: Include gene names, methods, datasets\n"
        prompt += "- Avoid REDUNDANCY: Check past tasks\n"
        prompt += "- Ensure FEASIBILITY: 30-90 minutes per task\n"
        prompt += "- Target HYPOTHESES: Especially unsupported ones\n\n"

        prompt += "Output your plan as valid JSON matching the format in the instructions.\n"

        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response to extract plan."""
        # Try to extract JSON
        if "```json" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_text = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_text = response_text

        try:
            plan = json.loads(json_text)
            return plan
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            # Try to extract tasks array
            import re
            tasks_match = re.search(r'"tasks"\s*:\s*\[(.*?)\]', json_text, re.DOTALL)
            if tasks_match:
                try:
                    tasks = json.loads(f"[{tasks_match.group(1)}]")
                    return {"tasks": tasks, "rationale": "Partially parsed plan"}
                except:
                    pass

            raise ValueError(f"Could not parse plan from response: {response_text[:500]}")

    def _validate_plan(self, plan: Dict[str, Any], expected_tasks: int) -> Dict[str, Any]:
        """Validate and fix plan structure."""
        if not isinstance(plan, dict):
            raise ValueError("Plan must be a dict")

        if "tasks" not in plan:
            raise ValueError("Plan must have 'tasks' key")

        tasks = plan["tasks"]
        if not isinstance(tasks, list):
            raise ValueError("Tasks must be a list")

        # Ensure each task has required fields
        validated_tasks = []
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                logger.warning(f"Skipping invalid task {i}: not a dict")
                continue

            # Fill in missing fields
            validated_task = {
                "id": task.get("id", i + 1),
                "type": task.get("type", "data_analysis"),
                "description": task.get("description", "No description provided"),
                "expected_output": task.get("expected_output", "Analysis results"),
                "target_hypotheses": task.get("target_hypotheses", []),
                "required_skills": task.get("required_skills", []),
                "estimated_time_minutes": task.get("estimated_time_minutes", 60),
                "exploration": task.get("exploration", True)
            }

            validated_tasks.append(validated_task)

        plan["tasks"] = validated_tasks

        # Ensure rationale exists
        if "rationale" not in plan:
            plan["rationale"] = "Research plan generated by Plan Creator"

        return plan

    def _fallback_plan(
        self,
        research_objective: str,
        context: Dict[str, Any],
        num_tasks: int
    ) -> Dict[str, Any]:
        """Generate fallback plan if LLM fails."""
        logger.warning("Using fallback plan generation")

        exploration_ratio = context.get('exploration_ratio', 0.5)
        num_exploration = int(num_tasks * exploration_ratio)
        num_exploitation = num_tasks - num_exploration

        tasks = []

        # Exploration tasks
        for i in range(num_exploration):
            tasks.append({
                "id": i + 1,
                "type": "hypothesis_generation" if i % 3 == 0 else "data_analysis",
                "description": f"Explore novel aspect {i+1} of {research_objective}",
                "expected_output": "New findings or hypotheses",
                "target_hypotheses": [],
                "required_skills": ["scikit-learn", "matplotlib"],
                "estimated_time_minutes": 60,
                "exploration": True
            })

        # Exploitation tasks
        unsupported = context.get('unsupported_hypotheses', [])
        for i in range(num_exploitation):
            if unsupported and i < len(unsupported):
                hyp = unsupported[i]
                tasks.append({
                    "id": num_exploration + i + 1,
                    "type": "data_analysis",
                    "description": f"Validate hypothesis: {hyp.get('text', 'Unknown')}",
                    "expected_output": "Statistical validation",
                    "target_hypotheses": [hyp.get('id', f'hyp_{i}')],
                    "required_skills": ["statsmodels", "scipy"],
                    "estimated_time_minutes": 75,
                    "exploration": False
                })
            else:
                tasks.append({
                    "id": num_exploration + i + 1,
                    "type": "literature_search",
                    "description": f"Search literature for evidence on {research_objective}",
                    "expected_output": "Literature summary",
                    "target_hypotheses": [],
                    "required_skills": ["pubmed-database"],
                    "estimated_time_minutes": 45,
                    "exploration": False
                })

        return {
            "tasks": tasks,
            "rationale": "Fallback plan: LLM generation failed, using template-based approach"
        }

    def revise_plan(
        self,
        original_plan: Dict[str, Any],
        feedback: str
    ) -> Dict[str, Any]:
        """
        Revise plan based on reviewer feedback.

        Args:
            original_plan: The plan that was rejected
            feedback: Feedback from Plan Reviewer

        Returns:
            Revised plan
        """
        logger.info("Revising plan based on feedback")

        # For now, just add a note that revision was attempted
        # In production, this would query LLM again with feedback
        original_plan["revised"] = True
        original_plan["revision_feedback"] = feedback

        return original_plan
