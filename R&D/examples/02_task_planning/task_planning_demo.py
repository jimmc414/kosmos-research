"""
Karpathy-Style Task Planning Demo for Kosmos

Demonstrates task generation strategy using patterns from:
- karpathy (Plan Creator, Plan Reviewer, delegation)
- scientific-skills (workflow templates)
- claude-skills-mcp (semantic similarity for novelty)

This solves Gap 2 (Task Generation Strategy) by showing how to:
1. Query State Manager for current knowledge
2. Generate 10 prioritized tasks using Plan Creator pattern
3. Validate tasks using Plan Reviewer pattern
4. Balance exploration vs exploitation
5. Detect redundant tasks using vector similarity
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List
import numpy as np


class MockStateManager:
    """
    Mock State Manager for demonstration

    In production, this would be the hybrid State Manager from
    R&D/examples/03_hybrid_state_manager/
    """

    def __init__(self):
        self.findings = [
            {
                "id": "finding_1",
                "summary": "BRCA1 is upregulated in cancer cells (p=0.001)",
                "cycle": 1,
                "validated": True
            },
            {
                "id": "finding_2",
                "summary": "TP53 mutation correlates with poor prognosis (p=0.005)",
                "cycle": 2,
                "validated": True
            },
            {
                "id": "finding_3",
                "summary": "Metabolic pathway enrichment in tumor cells",
                "cycle": 3,
                "validated": False
            }
        ]

        self.hypotheses = [
            {
                "id": "hyp_1",
                "text": "BRCA1 and TP53 form regulatory network",
                "validated": False,
                "evidence_count": 1
            },
            {
                "id": "hyp_2",
                "text": "Metabolic reprogramming drives cancer progression",
                "validated": False,
                "evidence_count": 0
            }
        ]

        self.completed_tasks = [
            {
                "cycle": 1,
                "task": 1,
                "description": "Analyze BRCA1 expression in single-cell data",
                "type": "data_analysis"
            },
            {
                "cycle": 1,
                "task": 2,
                "description": "Search literature for BRCA1-TP53 interactions",
                "type": "literature_search"
            },
            {
                "cycle": 2,
                "task": 1,
                "description": "Analyze TP53 mutation data",
                "type": "data_analysis"
            }
        ]

    def query_all(self) -> Dict:
        """Query all state"""
        return {
            "findings": self.findings,
            "hypotheses": self.hypotheses,
            "completed_tasks": self.completed_tasks
        }


class PlanCreatorAgent:
    """
    Plan Creator Agent (karpathy pattern)

    Generates research tasks based on current State Manager state
    """

    def __init__(self):
        # In production: would use Claude with scientific-skills context
        self.task_templates = {
            "data_analysis": [
                "Analyze {gene} expression in {dataset}",
                "Correlate {feature1} with {feature2} in {context}",
                "Compare {group1} vs {group2} using {method}"
            ],
            "literature_search": [
                "Search for papers on {topic} from {year_range}",
                "Find evidence for {hypothesis}",
                "Review {method} applications in {domain}"
            ],
            "hypothesis_generation": [
                "Generate hypotheses about {phenomenon}",
                "Propose mechanisms for {observation}"
            ]
        }

    async def create_plan(self, research_objective: str, context: Dict, num_tasks: int = 10) -> Dict:
        """
        Generate research plan with N tasks

        In production: This would use Claude Sonnet 4.5 with prompt:
        ```
        You are the Plan Creator for Kosmos AI Scientist.
        Research objective: {research_objective}
        Current state: {context}
        Generate {num_tasks} specific research tasks.
        Balance exploration (new directions) and exploitation (deepen findings).
        ```
        """
        exploration_ratio = context["exploration_ratio"]
        num_exploration = int(num_tasks * exploration_ratio)
        num_exploitation = num_tasks - num_exploration

        tasks = []

        # Exploration tasks (new directions)
        for i in range(num_exploration):
            task = {
                "id": i + 1,
                "type": "hypothesis_generation" if i % 3 == 0 else "data_analysis",
                "description": f"Explore novel aspect {i + 1} of {research_objective}",
                "expected_output": "New findings or hypotheses",
                "estimated_time": "30-60 minutes",
                "exploration": True
            }
            tasks.append(task)

        # Exploitation tasks (deepen existing findings)
        for i in range(num_exploitation):
            # Target unsupported hypotheses
            unsupported = [h for h in context.get("unsupported_hypotheses", [])]
            if unsupported and i < len(unsupported):
                hypothesis = unsupported[i]
                task = {
                    "id": num_exploration + i + 1,
                    "type": "data_analysis",
                    "description": f"Test hypothesis: {hypothesis['text']}",
                    "expected_output": "Statistical validation of hypothesis",
                    "target_hypotheses": [hypothesis['id']],
                    "estimated_time": "45-90 minutes",
                    "exploration": False
                }
            else:
                # Deepen recent findings
                task = {
                    "id": num_exploration + i + 1,
                    "type": "literature_search",
                    "description": f"Find additional evidence for finding {i + 1}",
                    "expected_output": "Supporting literature",
                    "estimated_time": "20-40 minutes",
                    "exploration": False
                }
            tasks.append(task)

        return {"tasks": tasks, "metadata": {"exploration_ratio": exploration_ratio}}


class PlanReviewerAgent:
    """
    Plan Reviewer Agent (karpathy pattern)

    Validates plan quality before execution
    """

    async def review_plan(self, plan: Dict, context: Dict) -> Dict:
        """
        Review plan for quality

        Criteria:
        1. Specificity: Are tasks concrete?
        2. Relevance: Do tasks advance objective?
        3. Novelty: Different from past tasks?
        4. Coverage: Diverse directions?
        5. Feasibility: Can be completed in time?
        """
        tasks = plan["tasks"]
        feedback = []
        approved = True

        # Check specificity
        vague_tasks = [t for t in tasks if len(t["description"]) < 20]
        if vague_tasks:
            feedback.append(f"Tasks {[t['id'] for t in vague_tasks]} are too vague")
            approved = False

        # Check for redundancy
        descriptions = [t["description"] for t in tasks]
        if len(descriptions) != len(set(descriptions)):
            feedback.append("Some tasks are redundant")
            approved = False

        # Check coverage
        types = [t["type"] for t in tasks]
        unique_types = set(types)
        if len(unique_types) < 2:
            feedback.append(f"Limited coverage: only {unique_types} task types")

        return {
            "approved": approved,
            "feedback": " | ".join(feedback) if feedback else "Plan looks good!",
            "suggestions": [
                "Consider adding more hypothesis generation tasks",
                "Ensure tasks have clear success criteria"
            ] if not approved else []
        }


class TaskGenerator:
    """
    Main Task Generator for Kosmos

    Combines Plan Creator + Plan Reviewer + novelty detection
    """

    def __init__(self, state_manager: MockStateManager):
        self.state_manager = state_manager
        self.plan_creator = PlanCreatorAgent()
        self.plan_reviewer = PlanReviewerAgent()

    async def generate_tasks(self, cycle_number: int, max_cycles: int = 20) -> List[Dict]:
        """Generate 10 prioritized tasks for this cycle"""

        # Step 1: Query State Manager for current knowledge
        current_state = self.state_manager.query_all()

        # Step 2: Create context for Plan Creator
        context = {
            "cycle": cycle_number,
            "findings_count": len(current_state["findings"]),
            "hypotheses_count": len(current_state["hypotheses"]),
            "recent_findings": current_state["findings"][-3:],  # Last 3
            "unsupported_hypotheses": [h for h in current_state["hypotheses"] if not h["validated"]],
            "past_tasks": current_state["completed_tasks"],
            "exploration_ratio": self._get_exploration_ratio(cycle_number, max_cycles)
        }

        # Step 3: Plan Creator generates tasks
        plan = await self.plan_creator.create_plan(
            research_objective="Discover novel mechanisms of cancer progression",
            context=context,
            num_tasks=10
        )

        # Step 4: Plan Reviewer validates quality
        review = await self.plan_reviewer.review_plan(plan, context)

        if not review["approved"]:
            print(f"⚠️  Plan needs revision: {review['feedback']}")
            # In production: would revise plan
            # For demo: proceed with warnings
        else:
            print(f"✓ Plan approved: {review['feedback']}")

        # Step 5: Prioritize tasks
        tasks = plan["tasks"]
        prioritized = self._prioritize_tasks(tasks, context)

        return prioritized

    def _get_exploration_ratio(self, cycle: int, max_cycles: int) -> float:
        """
        Exploration/exploitation balance (karpathy pattern)

        Early cycles: More exploration (discover new directions)
        Late cycles: More exploitation (deepen existing findings)
        """
        if cycle <= max_cycles // 2:
            return 0.7  # First half: 70% exploration
        else:
            return 0.3  # Second half: 30% exploration

    def _prioritize_tasks(self, tasks: List[Dict], context: Dict) -> List[Dict]:
        """
        Prioritize tasks based on novelty + gap scores

        Uses vector similarity (claude-skills-mcp pattern) for novelty
        """
        exploration_ratio = context["exploration_ratio"]

        for task in tasks:
            # Novelty score (0-1): How different from past tasks?
            novelty = self._compute_novelty(task, context["past_tasks"])

            # Gap score (0-1): How much does it fill knowledge gaps?
            gap_score = self._compute_gap_score(task, context["unsupported_hypotheses"])

            # Combined priority
            task["novelty"] = novelty
            task["gap_score"] = gap_score
            task["priority"] = (
                exploration_ratio * novelty +
                (1 - exploration_ratio) * gap_score
            )

        # Sort by priority (high to low)
        tasks.sort(key=lambda t: t["priority"], reverse=True)

        return tasks

    def _compute_novelty(self, task: Dict, past_tasks: List[Dict]) -> float:
        """
        Compute novelty using vector similarity (claude-skills-mcp pattern)

        In production: Use sentence-transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        task_embedding = model.encode(task["description"])
        past_embeddings = model.encode([t["description"] for t in past_tasks])
        similarities = cosine_similarity(task_embedding, past_embeddings)
        novelty = 1 - max(similarities)
        """
        # Mock implementation: simple string matching
        if not past_tasks:
            return 1.0  # Completely novel

        task_desc = task["description"].lower()
        max_similarity = 0.0

        for past_task in past_tasks:
            past_desc = past_task["description"].lower()
            # Simple overlap-based similarity
            task_words = set(task_desc.split())
            past_words = set(past_desc.split())
            overlap = len(task_words & past_words)
            similarity = overlap / max(len(task_words), len(past_words))
            max_similarity = max(max_similarity, similarity)

        return 1 - max_similarity

    def _compute_gap_score(self, task: Dict, unsupported_hypotheses: List[Dict]) -> float:
        """
        How well does this task address knowledge gaps?

        Higher score if:
        - Task tests unsupported hypotheses
        - Task targets areas with few findings
        """
        if task["type"] == "hypothesis_generation":
            # Hypothesis generation always addresses gaps
            return 0.8

        # Check if task targets unsupported hypotheses
        task_targets = task.get("target_hypotheses", [])
        unsupported_ids = [h["id"] for h in unsupported_hypotheses]

        if not task_targets:
            return 0.3  # Low gap score if no clear target

        overlap = len(set(task_targets) & set(unsupported_ids))
        return min(1.0, overlap / len(task_targets) + 0.3)


async def demo():
    """Demonstrate task planning pipeline"""
    print("=" * 80)
    print("TASK PLANNING PIPELINE DEMO (Karpathy Pattern)")
    print("=" * 80)
    print()

    # Initialize
    state_manager = MockStateManager()
    task_generator = TaskGenerator(state_manager)

    # Simulate multiple cycles
    for cycle in [1, 5, 10, 15, 20]:
        print(f"\n{'=' * 80}")
        print(f"CYCLE {cycle} TASK GENERATION")
        print('=' * 80)

        # Generate tasks
        tasks = await task_generator.generate_tasks(cycle_number=cycle, max_cycles=20)

        # Display results
        exploration_ratio = task_generator._get_exploration_ratio(cycle, 20)
        print(f"\nExploration ratio: {exploration_ratio:.1%}")
        print(f"Generated {len(tasks)} prioritized tasks:\n")

        for i, task in enumerate(tasks, 1):
            print(f"{i}. [{task['type'].upper()}] {task['description']}")
            print(f"   Priority: {task['priority']:.2f} "
                  f"(Novelty: {task['novelty']:.2f}, Gap: {task['gap_score']:.2f})")
            if task.get('target_hypotheses'):
                print(f"   Targets: {task['target_hypotheses']}")
            print()

    print("=" * 80)
    print("KEY PATTERNS DEMONSTRATED")
    print("=" * 80)
    print()
    print("1. Plan Creator Agent (karpathy)")
    print("   - Generates tasks based on State Manager state")
    print("   - Balances exploration vs exploitation")
    print()
    print("2. Plan Reviewer Agent (karpathy)")
    print("   - Validates task quality before execution")
    print("   - Provides feedback for revision")
    print()
    print("3. Novelty Detection (claude-skills-mcp)")
    print("   - Uses vector similarity to avoid redundant tasks")
    print("   - Ensures fresh research directions")
    print()
    print("4. Strategic Prioritization")
    print("   - Early cycles: 70% exploration (discover)")
    print("   - Late cycles: 30% exploration (exploit)")
    print()
    print("5. Gap-Based Targeting")
    print("   - Prioritizes tasks that test unsupported hypotheses")
    print("   - Fills knowledge gaps systematically")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demo())
