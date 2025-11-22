"""
End-to-End Research Workflow Demo.

This demonstrates the complete Kosmos autonomous research system integrating
all Phase 1 + Phase 2 components:

- Plan Creator/Reviewer (karpathy orchestration)
- Delegation Manager (task execution)
- Novelty Detector (redundancy prevention)
- Data Analyst with Skills (domain expertise)
- ScholarEval (discovery validation)
- Context Compressor (memory management)
- Artifact State Manager (persistent storage)

This runs a mini research project (5 cycles instead of 20) to validate
all components working together.

Usage:
    python research_workflow_demo.py

Expected runtime: ~15-20 minutes for 5 cycles
"""

import asyncio
import sys
from pathlib import Path

# Add kosmos to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "kosmos"))

from kosmos.workflow import ResearchWorkflow


async def main():
    """Run demo research workflow."""

    print("=" * 80)
    print("KOSMOS END-TO-END RESEARCH WORKFLOW DEMO")
    print("=" * 80)
    print()
    print("This demo will run 5 research cycles (vs 20 in production)")
    print("to demonstrate the complete autonomous research system.")
    print()
    print("Components integrated:")
    print("  - Plan Creator/Reviewer (orchestration)")
    print("  - Delegation Manager (execution)")
    print("  - Novelty Detector (redundancy prevention)")
    print("  - Data Analyst + Skills (domain expertise)")
    print("  - ScholarEval (quality validation)")
    print("  - Context Compressor (memory management)")
    print("  - Artifact State Manager (storage)")
    print()
    print("=" * 80)
    print()

    # Initialize workflow
    workflow = ResearchWorkflow(
        research_objective=(
            "Investigate metabolic reprogramming in cancer cells. "
            "Specifically, identify key metabolic pathways that are altered "
            "in cancer cells compared to normal cells, and explore potential "
            "therapeutic targets for metabolic intervention. Focus on glycolysis, "
            "oxidative phosphorylation, and amino acid metabolism."
        ),
        output_dir="./demo_output",
        min_plan_score=7.0,
        min_discovery_score=0.75,
        max_parallel_tasks=3,
        enable_novelty_detection=True,
        enable_scholar_eval=True
    )

    print("✓ Workflow initialized")
    print()

    # Run 5 cycles for demo
    print("Starting 5-cycle research workflow...")
    print("(Full production run would be 20 cycles)")
    print()

    try:
        results = await workflow.run(num_cycles=5, tasks_per_cycle=10)

        # Display results
        print()
        print("=" * 80)
        print("RESEARCH WORKFLOW COMPLETE")
        print("=" * 80)
        print()
        print(f"Research Objective: {results['research_objective']}")
        print()
        print("RESULTS:")
        print(f"  Total Cycles: {results['total_cycles']}")
        print(f"  Total Tasks: {results['total_tasks_executed']}")
        print(f"  Total Findings: {results['total_findings']}")
        print(f"  Validated Findings: {results['validated_findings']}")
        print(f"  Validation Rate: {results['validation_rate']:.1%}")
        print()
        print(f"OUTPUT:")
        print(f"  Directory: {results['output_dir']}")
        print(f"  Final Report: {results['final_report_path']}")
        print()

        # Cycle-by-cycle summary
        print("CYCLE SUMMARY:")
        print("-" * 80)
        print(f"{'Cycle':<8} {'Status':<12} {'Tasks':<8} {'Findings':<10} {'Validated':<12} {'Score':<8}")
        print("-" * 80)

        for cycle in results['cycle_summaries']:
            if cycle.get('status') == 'completed':
                print(
                    f"{cycle['cycle']:<8} "
                    f"{cycle['status']:<12} "
                    f"{cycle.get('tasks_completed', 0):<8} "
                    f"{cycle.get('new_findings', 0):<10} "
                    f"{cycle.get('validated_findings', 0):<12} "
                    f"{cycle.get('plan_score', 0):.1f}/10"
                )
            else:
                print(
                    f"{cycle['cycle']:<8} "
                    f"{cycle.get('status', 'unknown'):<12} "
                    f"ERROR: {cycle.get('error', 'Unknown error')}"
                )

        print("-" * 80)
        print()

        # Quality metrics
        avg_plan_score = sum(
            c.get('plan_score', 0) for c in results['cycle_summaries']
            if c.get('status') == 'completed'
        ) / len([c for c in results['cycle_summaries'] if c.get('status') == 'completed'])

        print("QUALITY METRICS:")
        print(f"  Average Plan Score: {avg_plan_score:.1f}/10")
        print(f"  Discovery Validation Rate: {results['validation_rate']:.1%}")
        print(f"  Task Success Rate: {results['total_findings'] / results['total_tasks_executed']:.1%}")
        print()

        # Next steps
        print("NEXT STEPS:")
        print(f"  1. Review final report: {results['final_report_path']}")
        print(f"  2. Explore cycle artifacts: {results['output_dir']}/artifacts/")
        print(f"  3. Check cycle summaries for detailed findings")
        print()
        print("For production use, increase num_cycles to 20 and enable")
        print("all validation components.")
        print()

        return 0

    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR: Research workflow failed")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        print("This is a demo - errors may occur due to:")
        print("  - Missing dependencies (sentence-transformers, etc.)")
        print("  - LLM API configuration")
        print("  - Insufficient resources")
        print()
        print("Check logs above for details.")
        print()

        return 1


def run_simple_test():
    """
    Simple non-async test of orchestration components.

    This can be run without async support to test individual components.
    """
    print("=" * 80)
    print("SIMPLE COMPONENT TEST (Non-async)")
    print("=" * 80)
    print()

    # Test imports
    print("Testing component imports...")

    try:
        from kosmos.orchestration import (
            PlanCreatorAgent,
            PlanReviewerAgent,
            DelegationManager,
            NoveltyDetector
        )
        print("  ✓ Orchestration components")

        from kosmos.workflow import ResearchWorkflow
        print("  ✓ Research workflow")

        from kosmos.validation.scholar_eval import ScholarEvalValidator
        print("  ✓ ScholarEval validator")

        from kosmos.compression import ContextCompressor
        print("  ✓ Context compressor")

        from kosmos.world_model.artifacts import ArtifactStateManager
        print("  ✓ Artifact state manager")

        from kosmos.agents.skill_loader import SkillLoader
        print("  ✓ Skill loader")

        print()
        print("All components imported successfully!")
        print()

        # Test NoveltyDetector (non-async)
        print("Testing Novelty Detector...")
        detector = NoveltyDetector(novelty_threshold=0.75)

        # Index some test tasks
        test_tasks = [
            {"id": 1, "type": "data_analysis", "description": "Analyze gene expression in cancer samples"},
            {"id": 2, "type": "literature_review", "description": "Review papers on cancer metabolism"},
            {"id": 3, "type": "data_analysis", "description": "Perform differential expression analysis"}
        ]

        detector.index_past_tasks(test_tasks)
        print(f"  ✓ Indexed {len(test_tasks)} past tasks")

        # Check novelty of a new task
        new_task = {"type": "data_analysis", "description": "Analyze differential gene expression patterns"}

        novelty = detector.check_task_novelty(new_task)
        print(f"  ✓ Novelty check: score={novelty['novelty_score']:.2f}, novel={novelty['is_novel']}")

        if novelty['similar_tasks']:
            print(f"    Similar to: {novelty['similar_tasks'][0]['task']['description'][:50]}...")

        print()
        print("Novelty detector working correctly!")
        print()

        # Test SkillLoader (non-async)
        print("Testing Skill Loader...")

        try:
            skill_loader = SkillLoader()
            available_skills = skill_loader.get_available_skills()

            if available_skills:
                print(f"  ✓ Found {len(available_skills)} scientific skills")
                print(f"    Examples: {', '.join(available_skills[:5])}")
            else:
                print("  ⚠ No skills found (kosmos-claude-scientific-skills may not be installed)")

            task_types = skill_loader.get_task_types()
            print(f"  ✓ Supported task types: {len(task_types)}")
            print(f"    Examples: {', '.join(task_types[:3])}")

        except Exception as e:
            print(f"  ⚠ Skill loader error: {e}")
            print("    (This is OK - skills are optional)")

        print()
        print("Component tests complete!")
        print()

        return 0

    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        print()
        print("Make sure kosmos is installed:")
        print("  cd R&D/kosmos && poetry install")
        print()
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kosmos End-to-End Workflow Demo")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run simple component test instead of full workflow"
    )

    args = parser.parse_args()

    if args.test:
        # Run simple test
        exit_code = run_simple_test()
    else:
        # Run full async workflow
        exit_code = asyncio.run(main())

    sys.exit(exit_code)
