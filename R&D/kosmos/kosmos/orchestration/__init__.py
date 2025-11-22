"""
Orchestration Module for Kosmos.

This module implements karpathy-style orchestration patterns for autonomous
research coordination. It provides Plan Creator and Plan Reviewer agents
for strategic task planning and execution.

Pattern source: R&D/kosmos-karpathy
Gap addressed: Gap 2 (Task Generation Strategy)

Key components:
- PlanCreatorAgent: Generates research plans with 10 prioritized tasks
- PlanReviewerAgent: Validates plan quality before execution
- DelegationManager: Coordinates expert agent execution
- NoveltyDetector: Detects redundant tasks using vector embeddings
- instructions.yaml: Agent prompts and behavior definitions

Usage:
    from kosmos.orchestration import (
        PlanCreatorAgent, PlanReviewerAgent,
        DelegationManager, NoveltyDetector
    )

    # Create plan
    creator = PlanCreatorAgent()
    plan = await creator.create_plan(research_objective, context)

    # Check novelty
    detector = NoveltyDetector()
    detector.index_past_tasks(context['past_tasks'])
    novelty = detector.check_plan_novelty(plan)

    # Review plan
    reviewer = PlanReviewerAgent()
    review = await reviewer.review_plan(plan, context)

    if review['approved']:
        # Execute tasks
        manager = DelegationManager()
        results = await manager.execute_plan(plan, cycle, context)
"""

from .plan_creator import PlanCreatorAgent
from .plan_reviewer import PlanReviewerAgent
from .delegation import DelegationManager
from .novelty_detector import NoveltyDetector

__all__ = [
    "PlanCreatorAgent",
    "PlanReviewerAgent",
    "DelegationManager",
    "NoveltyDetector"
]
