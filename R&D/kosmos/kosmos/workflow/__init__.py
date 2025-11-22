"""
Research Workflow Module for Kosmos.

This module implements the end-to-end research loop that coordinates all
Kosmos components to autonomously conduct scientific research.

Key components integrated:
- Plan Creator/Reviewer (karpathy orchestration)
- Delegation Manager (task execution)
- Novelty Detector (redundancy prevention)
- Data Analyst with Skills (domain expertise)
- ScholarEval (discovery validation)
- Context Compressor (memory management)
- Artifact State Manager (persistent storage)

Usage:
    from kosmos.workflow import ResearchWorkflow

    workflow = ResearchWorkflow(research_objective="...")
    results = await workflow.run(num_cycles=20)
"""

from .research_loop import ResearchWorkflow

__all__ = ["ResearchWorkflow"]
