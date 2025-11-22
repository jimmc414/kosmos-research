"""
Delegation Manager for Kosmos Orchestration.

This component coordinates execution of approved research plans by dispatching
tasks to specialized agents and collecting results.

Pattern source: R&D/kosmos-karpathy
Gap addressed: Gap 2 (Task Generation Strategy)
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import yaml

from kosmos.core.llm import get_client

logger = logging.getLogger(__name__)


class DelegationManager:
    """
    Manages delegation and execution of research tasks.

    This orchestrates the execution of approved plans by:
    1. Dispatching tasks to specialized agents
    2. Tracking execution status
    3. Collecting and validating results
    4. Handling retries and failures
    """

    def __init__(
        self,
        max_parallel_tasks: int = 3,
        max_retries: int = 2,
        task_timeout_minutes: int = 120
    ):
        """
        Initialize delegation manager.

        Args:
            max_parallel_tasks: Max tasks to run in parallel
            max_retries: Max retry attempts for failed tasks
            task_timeout_minutes: Timeout for task execution
        """
        self.client = get_client()
        self.max_parallel_tasks = max_parallel_tasks
        self.max_retries = max_retries
        self.task_timeout_seconds = task_timeout_minutes * 60

        # Load agent instructions
        instructions_path = Path(__file__).parent / "instructions.yaml"
        with open(instructions_path) as f:
            instructions = yaml.safe_load(f)
            self.instructions = instructions

        # Task execution tracking
        self.task_status: Dict[str, str] = {}  # task_id -> status
        self.task_results: Dict[str, Dict] = {}  # task_id -> result
        self.task_retries: Dict[str, int] = {}  # task_id -> retry_count

    async def execute_plan(
        self,
        plan: Dict[str, Any],
        cycle: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a research plan.

        Args:
            plan: Approved plan from Plan Creator/Reviewer
            cycle: Current research cycle number
            context: Current research state

        Returns:
            Dict with:
                - completed_tasks: List of completed task results
                - failed_tasks: List of failed tasks
                - execution_summary: Summary statistics
        """
        tasks = plan.get("tasks", [])
        logger.info(f"Executing plan with {len(tasks)} tasks for cycle {cycle}")

        # Initialize tracking
        for task in tasks:
            task_id = task.get("id", "unknown")
            self.task_status[task_id] = "pending"
            self.task_retries[task_id] = 0

        # Execute tasks in batches to respect parallel limit
        completed_tasks = []
        failed_tasks = []

        # Group tasks by priority (if available) or maintain order
        task_batches = self._create_task_batches(tasks)

        for batch in task_batches:
            logger.info(f"Executing batch of {len(batch)} tasks")

            # Execute batch in parallel
            batch_results = await asyncio.gather(
                *[self._execute_task(task, cycle, context) for task in batch],
                return_exceptions=True
            )

            # Process results
            for task, result in zip(batch, batch_results):
                task_id = task.get("id", "unknown")

                if isinstance(result, Exception):
                    logger.error(f"Task {task_id} failed with exception: {result}")

                    # Retry if under limit
                    if self.task_retries[task_id] < self.max_retries:
                        self.task_retries[task_id] += 1
                        logger.info(f"Retrying task {task_id} (attempt {self.task_retries[task_id]})")

                        retry_result = await self._execute_task(task, cycle, context)

                        if isinstance(retry_result, Exception):
                            self.task_status[task_id] = "failed"
                            failed_tasks.append({
                                "task": task,
                                "error": str(retry_result)
                            })
                        else:
                            self.task_status[task_id] = "completed"
                            completed_tasks.append(retry_result)
                    else:
                        self.task_status[task_id] = "failed"
                        failed_tasks.append({
                            "task": task,
                            "error": str(result)
                        })
                else:
                    self.task_status[task_id] = "completed"
                    completed_tasks.append(result)

        # Generate execution summary
        summary = self._generate_execution_summary(
            completed_tasks,
            failed_tasks,
            cycle
        )

        logger.info(
            f"Plan execution complete: "
            f"{len(completed_tasks)} succeeded, {len(failed_tasks)} failed"
        )

        return {
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "execution_summary": summary
        }

    def _create_task_batches(self, tasks: List[Dict]) -> List[List[Dict]]:
        """
        Create batches of tasks for parallel execution.

        Respects max_parallel_tasks limit and tries to group independent tasks.
        """
        batches = []
        current_batch = []

        for task in tasks:
            current_batch.append(task)

            if len(current_batch) >= self.max_parallel_tasks:
                batches.append(current_batch)
                current_batch = []

        # Add remaining tasks
        if current_batch:
            batches.append(current_batch)

        return batches

    async def _execute_task(
        self,
        task: Dict[str, Any],
        cycle: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single task by delegating to appropriate agent.

        Args:
            task: Task specification
            cycle: Current cycle
            context: Research context

        Returns:
            Task result dict
        """
        task_id = task.get("id", "unknown")
        task_type = task.get("type", "unknown")

        logger.info(f"Executing task {task_id} (type: {task_type})")

        self.task_status[task_id] = "running"
        start_time = datetime.utcnow()

        try:
            # Delegate to appropriate agent based on task type
            if task_type == "data_analysis":
                result = await self._execute_data_analysis(task, cycle, context)
            elif task_type == "literature_review":
                result = await self._execute_literature_review(task, cycle, context)
            elif task_type == "hypothesis_generation":
                result = await self._execute_hypothesis_generation(task, cycle, context)
            elif task_type == "experiment_design":
                result = await self._execute_experiment_design(task, cycle, context)
            elif task_type == "code_development":
                result = await self._execute_code_development(task, cycle, context)
            else:
                # Generic task execution
                result = await self._execute_generic_task(task, cycle, context)

            # Add metadata
            result["task_id"] = task_id
            result["task_type"] = task_type
            result["cycle"] = cycle
            result["execution_time_seconds"] = (datetime.utcnow() - start_time).total_seconds()
            result["completed_at"] = datetime.utcnow().isoformat()

            logger.info(f"Task {task_id} completed successfully")

            return result

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            raise

    async def _execute_data_analysis(
        self,
        task: Dict[str, Any],
        cycle: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute data analysis task using Data Analyst agent.

        This uses the data_analyst instructions from instructions.yaml
        and can integrate with the SkillLoader for domain expertise.
        """
        instruction = self.instructions.get("data_analyst", "")

        # Build prompt
        prompt = f"{instruction}\n\n"
        prompt += "=" * 80 + "\n"
        prompt += "TASK SPECIFICATION\n"
        prompt += "=" * 80 + "\n\n"
        prompt += f"**Task ID**: {task.get('id')}\n"
        prompt += f"**Description**: {task.get('description')}\n"
        prompt += f"**Expected Output**: {task.get('expected_output')}\n\n"

        if task.get("required_skills"):
            prompt += f"**Required Skills**: {', '.join(task.get('required_skills'))}\n\n"

        if task.get("data_sources"):
            prompt += f"**Data Sources**: {task.get('data_sources')}\n\n"

        # Add context
        prompt += "**Research Context**:\n"
        prompt += f"- Cycle: {cycle}/20\n"
        prompt += f"- Current Findings: {len(context.get('findings', []))}\n"
        prompt += f"- Research Objective: {context.get('research_objective', 'Not specified')}\n\n"

        # Recent findings for context
        recent_findings = context.get("findings", [])[-5:]
        if recent_findings:
            prompt += "**Recent Findings** (for context):\n"
            for i, finding in enumerate(recent_findings, 1):
                prompt += f"{i}. {finding.get('summary', 'No summary')}\n"
            prompt += "\n"

        prompt += "=" * 80 + "\n"
        prompt += "EXECUTE THE TASK\n"
        prompt += "=" * 80 + "\n\n"
        prompt += "Perform the analysis and return your findings in JSON format:\n"
        prompt += "{\n"
        prompt += '  "summary": "2-line summary of key finding",\n'
        prompt += '  "statistics": {"p_value": <float>, "confidence": <float>, ...},\n'
        prompt += '  "methods": "Brief description of methods used",\n'
        prompt += '  "code_snippet": "Key code used (if applicable)",\n'
        prompt += '  "interpretation": "What this means for the research",\n'
        prompt += '  "next_steps": ["suggestion 1", "suggestion 2"]\n'
        prompt += "}\n"

        # Query LLM
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=messages,
                temperature=0.5
            )

            # Parse response
            import json
            response_text = response.content[0].text

            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_text = response_text

            result = json.loads(json_text)

            # Ensure required fields
            if "summary" not in result:
                result["summary"] = "Analysis completed (no summary provided)"
            if "statistics" not in result:
                result["statistics"] = {}

            return result

        except Exception as e:
            logger.error(f"Data analysis task failed: {e}")
            # Return minimal result
            return {
                "summary": f"Task {task.get('id')} execution failed: {str(e)}",
                "statistics": {},
                "error": str(e)
            }

    async def _execute_literature_review(
        self,
        task: Dict[str, Any],
        cycle: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute literature review task using Literature Analyzer agent.
        """
        instruction = self.instructions.get("literature_analyzer", "")

        # Build prompt
        prompt = f"{instruction}\n\n"
        prompt += "=" * 80 + "\n"
        prompt += "LITERATURE REVIEW TASK\n"
        prompt += "=" * 80 + "\n\n"
        prompt += f"**Task**: {task.get('description')}\n"
        prompt += f"**Focus**: {task.get('focus', 'General review')}\n\n"

        if task.get("keywords"):
            prompt += f"**Keywords**: {', '.join(task.get('keywords'))}\n\n"

        prompt += "Conduct the literature review and return findings in JSON format:\n"
        prompt += "{\n"
        prompt += '  "summary": "Key insights from literature",\n'
        prompt += '  "relevant_papers": [{"title": "...", "finding": "...", "relevance": "..."}, ...],\n'
        prompt += '  "gaps_identified": ["gap 1", "gap 2"],\n'
        prompt += '  "recommendations": ["recommendation 1", "recommendation 2"]\n'
        prompt += "}\n"

        # Query LLM
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=messages,
                temperature=0.4
            )

            # Parse response
            import json
            response_text = response.content[0].text

            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_text = response_text

            result = json.loads(json_text)
            return result

        except Exception as e:
            logger.error(f"Literature review task failed: {e}")
            return {
                "summary": f"Literature review failed: {str(e)}",
                "relevant_papers": [],
                "gaps_identified": [],
                "recommendations": [],
                "error": str(e)
            }

    async def _execute_hypothesis_generation(
        self,
        task: Dict[str, Any],
        cycle: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute hypothesis generation task."""
        # Use research_director instruction for hypothesis generation
        instruction = self.instructions.get("research_director", "")

        prompt = f"{instruction}\n\n"
        prompt += "Generate new hypotheses based on current research state.\n\n"
        prompt += f"**Task**: {task.get('description')}\n"
        prompt += f"**Current Findings**: {len(context.get('findings', []))}\n\n"

        # Add recent findings
        recent_findings = context.get("findings", [])[-10:]
        if recent_findings:
            prompt += "**Recent Findings**:\n"
            for finding in recent_findings:
                prompt += f"- {finding.get('summary', 'No summary')}\n"
            prompt += "\n"

        prompt += "Generate 3-5 new, testable hypotheses in JSON format:\n"
        prompt += "{\n"
        prompt += '  "hypotheses": [\n'
        prompt += '    {"hypothesis": "...", "rationale": "...", "testability": "high/medium/low"},\n'
        prompt += '    ...\n'
        prompt += '  ]\n'
        prompt += "}\n"

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=messages,
                temperature=0.7  # Higher for creativity
            )

            import json
            response_text = response.content[0].text

            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_text = response_text

            result = json.loads(json_text)
            result["summary"] = f"Generated {len(result.get('hypotheses', []))} new hypotheses"
            return result

        except Exception as e:
            logger.error(f"Hypothesis generation failed: {e}")
            return {
                "summary": f"Hypothesis generation failed: {str(e)}",
                "hypotheses": [],
                "error": str(e)
            }

    async def _execute_experiment_design(
        self,
        task: Dict[str, Any],
        cycle: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute experiment design task."""
        instruction = self.instructions.get("common_instructions", "")

        prompt = f"{instruction}\n\n"
        prompt += "Design an experiment to test a hypothesis.\n\n"
        prompt += f"**Task**: {task.get('description')}\n"
        prompt += f"**Hypothesis**: {task.get('hypothesis', 'Not specified')}\n\n"

        prompt += "Design the experiment and return in JSON format:\n"
        prompt += "{\n"
        prompt += '  "summary": "Experiment design overview",\n'
        prompt += '  "design": {\n'
        prompt += '    "approach": "...",\n'
        prompt += '    "methods": "...",\n'
        prompt += '    "controls": "...",\n'
        prompt += '    "sample_size": "..."\n'
        prompt += '  },\n'
        prompt += '  "expected_outcomes": ["outcome 1", "outcome 2"],\n'
        prompt += '  "resources_needed": ["resource 1", "resource 2"]\n'
        prompt += "}\n"

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                messages=messages,
                temperature=0.6
            )

            import json
            response_text = response.content[0].text

            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            else:
                json_text = response_text

            return json.loads(json_text)

        except Exception as e:
            logger.error(f"Experiment design failed: {e}")
            return {
                "summary": f"Experiment design failed: {str(e)}",
                "design": {},
                "error": str(e)
            }

    async def _execute_code_development(
        self,
        task: Dict[str, Any],
        cycle: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute code development task."""
        # Similar to data_analysis but focused on code generation
        return await self._execute_data_analysis(task, cycle, context)

    async def _execute_generic_task(
        self,
        task: Dict[str, Any],
        cycle: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute generic task with common instructions."""
        instruction = self.instructions.get("common_instructions", "")

        prompt = f"{instruction}\n\n"
        prompt += f"**Task**: {task.get('description')}\n"
        prompt += f"**Expected Output**: {task.get('expected_output', 'Analysis and findings')}\n\n"
        prompt += "Execute the task and return findings in JSON format.\n"

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=messages,
                temperature=0.5
            )

            import json
            response_text = response.content[0].text

            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            else:
                # Try to extract any JSON
                try:
                    return json.loads(response_text)
                except:
                    # Return as summary
                    return {
                        "summary": response_text[:500],
                        "full_response": response_text
                    }

            return json.loads(json_text)

        except Exception as e:
            logger.error(f"Generic task execution failed: {e}")
            return {
                "summary": f"Task execution failed: {str(e)}",
                "error": str(e)
            }

    def _generate_execution_summary(
        self,
        completed_tasks: List[Dict],
        failed_tasks: List[Dict],
        cycle: int
    ) -> Dict[str, Any]:
        """Generate summary of plan execution."""
        total_tasks = len(completed_tasks) + len(failed_tasks)

        # Count task types
        task_types = {}
        for task_result in completed_tasks:
            task_type = task_result.get("task_type", "unknown")
            task_types[task_type] = task_types.get(task_type, 0) + 1

        # Calculate average execution time
        execution_times = [
            t.get("execution_time_seconds", 0)
            for t in completed_tasks
            if "execution_time_seconds" in t
        ]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0

        summary = {
            "cycle": cycle,
            "total_tasks": total_tasks,
            "completed": len(completed_tasks),
            "failed": len(failed_tasks),
            "success_rate": len(completed_tasks) / total_tasks if total_tasks > 0 else 0,
            "task_types": task_types,
            "average_execution_time_seconds": round(avg_time, 1),
            "total_execution_time_seconds": round(sum(execution_times), 1)
        }

        return summary

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get current status of a task."""
        return self.task_status.get(task_id)

    def get_task_result(self, task_id: str) -> Optional[Dict]:
        """Get result of a completed task."""
        return self.task_results.get(task_id)

    def reset(self):
        """Reset tracking for new plan execution."""
        self.task_status.clear()
        self.task_results.clear()
        self.task_retries.clear()
