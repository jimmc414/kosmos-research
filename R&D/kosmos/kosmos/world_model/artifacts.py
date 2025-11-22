"""
Artifact-based State Manager Extension for Kosmos.

This module implements the artifact-based persistence pattern from karpathy,
providing human-readable JSON files alongside the graph database for:
- Easier debugging
- Version control compatibility
- Human review capability
- Complete audit trail

Pattern source: R&D/kosmos-karpathy (artifact-based communication)
Gap addressed: Gap 1 (State Manager Architecture)

Architecture:
    sandbox/
    ├── cycle_1/
    │   ├── task_1_findings.json
    │   ├── task_1_notebook.ipynb
    │   ├── task_2_findings.json
    │   └── cycle_1_summary.md
    ├── cycle_2/
    │   └── ...
    └── final_synthesis.md

Usage:
    manager = ArtifactStateManager(sandbox_dir="sandbox")

    # Save finding as artifact + index to graph
    await manager.save_finding_artifact(
        cycle=1, task=1, finding=finding_data
    )

    # Load finding from artifact
    finding = manager.load_finding_artifact(cycle=1, task=1)

    # Generate cycle summary
    summary = await manager.generate_cycle_summary(cycle=1)
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from kosmos.world_model.interface import WorldModelStorage
from kosmos.world_model.models import Entity, Relationship

logger = logging.getLogger(__name__)


class ArtifactStateManager:
    """
    Artifact-based persistence layer for State Manager.

    This complements the graph database with human-readable JSON files,
    implementing the karpathy pattern of artifact-based communication.

    Benefits:
    - Human-readable for debugging
    - Version control compatible
    - Complete audit trail
    - Can be reviewed/edited manually
    - Survives database resets

    This works alongside WorldModelStorage, not instead of it.
    Artifacts are the source of truth, graph is for querying.
    """

    def __init__(
        self,
        sandbox_dir: str = "sandbox",
        world_model: Optional[WorldModelStorage] = None
    ):
        """
        Initialize artifact manager.

        Args:
            sandbox_dir: Root directory for artifacts
            world_model: Optional world model for graph indexing
        """
        self.sandbox = Path(sandbox_dir)
        self.sandbox.mkdir(exist_ok=True, parents=True)
        self.world_model = world_model

    def get_cycle_dir(self, cycle: int) -> Path:
        """Get directory for a specific cycle."""
        cycle_dir = self.sandbox / f"cycle_{cycle}"
        cycle_dir.mkdir(exist_ok=True, parents=True)
        return cycle_dir

    async def save_finding_artifact(
        self,
        cycle: int,
        task: int,
        finding: Dict[str, Any],
        index_to_graph: bool = True
    ) -> Path:
        """
        Save finding as JSON artifact.

        Args:
            cycle: Cycle number
            task: Task number
            finding: Finding data dict with keys:
                - id: Finding ID
                - summary: 2-line summary
                - statistics: Dict of stats (p_value, confidence, etc.)
                - notebook_path: Path to Jupyter notebook
                - timestamp: ISO timestamp
                - citations: List of paper citations (optional)
                - supports_hypothesis: Hypothesis ID (optional)
                - refutes_hypothesis: Hypothesis ID (optional)
            index_to_graph: Whether to index to graph database

        Returns:
            Path to artifact file
        """
        cycle_dir = self.get_cycle_dir(cycle)

        # Create artifact
        artifact = {
            "finding_id": finding["id"],
            "cycle": cycle,
            "task": task,
            "summary": finding["summary"],
            "statistics": finding.get("statistics", {}),
            "notebook_path": str(finding.get("notebook_path", "")),
            "timestamp": finding.get("timestamp", datetime.utcnow().isoformat()),
            "citations": finding.get("citations", []),
            "supports_hypothesis": finding.get("supports_hypothesis"),
            "refutes_hypothesis": finding.get("refutes_hypothesis"),
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "artifact_version": "1.0"
            }
        }

        # Save to file
        artifact_path = cycle_dir / f"task_{task}_finding.json"
        with open(artifact_path, "w") as f:
            json.dump(artifact, f, indent=2)

        logger.info(f"Saved finding artifact: {artifact_path}")

        # Optionally index to graph
        if index_to_graph and self.world_model:
            await self._index_finding_to_graph(artifact)

        return artifact_path

    async def _index_finding_to_graph(self, artifact: Dict[str, Any]):
        """Index finding artifact to graph database."""
        # Create entity
        entity = Entity(
            id=artifact["finding_id"],
            type="Finding",
            properties={
                "summary": artifact["summary"],
                "cycle": artifact["cycle"],
                "task": artifact["task"],
                "p_value": artifact["statistics"].get("p_value"),
                "confidence": artifact["statistics"].get("confidence"),
                "notebook_path": artifact["notebook_path"],
                "timestamp": artifact["timestamp"]
            },
            confidence=artifact["statistics"].get("confidence", 0.5),
            source=f"data_analysis_cycle_{artifact['cycle']}"
        )

        self.world_model.add_entity(entity, merge=True)

        # Create relationships
        if artifact.get("supports_hypothesis"):
            rel = Relationship(
                source_id=artifact["finding_id"],
                target_id=artifact["supports_hypothesis"],
                type="SUPPORTS",
                properties={"confidence": artifact["statistics"].get("confidence", 0.5)},
                source="data_analysis"
            )
            self.world_model.add_relationship(rel)

        if artifact.get("refutes_hypothesis"):
            rel = Relationship(
                source_id=artifact["finding_id"],
                target_id=artifact["refutes_hypothesis"],
                type="REFUTES",
                properties={"confidence": artifact["statistics"].get("confidence", 0.5)},
                source="data_analysis"
            )
            self.world_model.add_relationship(rel)

        # Track citations
        for citation in artifact.get("citations", []):
            citation_entity = Entity(
                id=citation.get("pmid", citation.get("doi", f"paper_{hash(citation['title'])}")),
                type="Paper",
                properties={
                    "title": citation.get("title", ""),
                    "authors": citation.get("authors", ""),
                    "pmid": citation.get("pmid"),
                    "doi": citation.get("doi")
                },
                source="literature_search"
            )
            self.world_model.add_entity(citation_entity, merge=True)

            # Link finding to paper
            cites_rel = Relationship(
                source_id=artifact["finding_id"],
                target_id=citation_entity.id,
                type="CITES",
                source="literature_search"
            )
            self.world_model.add_relationship(cites_rel)

    def load_finding_artifact(self, cycle: int, task: int) -> Optional[Dict[str, Any]]:
        """
        Load finding artifact from file.

        Args:
            cycle: Cycle number
            task: Task number

        Returns:
            Finding dict or None if not found
        """
        cycle_dir = self.get_cycle_dir(cycle)
        artifact_path = cycle_dir / f"task_{task}_finding.json"

        if not artifact_path.exists():
            logger.warning(f"Artifact not found: {artifact_path}")
            return None

        with open(artifact_path) as f:
            return json.load(f)

    def get_all_cycle_findings(self, cycle: int) -> List[Dict[str, Any]]:
        """
        Get all findings for a cycle.

        Args:
            cycle: Cycle number

        Returns:
            List of finding dicts
        """
        cycle_dir = self.get_cycle_dir(cycle)

        findings = []
        for artifact_file in sorted(cycle_dir.glob("task_*_finding.json")):
            with open(artifact_file) as f:
                findings.append(json.load(f))

        return findings

    async def generate_cycle_summary(self, cycle: int) -> str:
        """
        Generate markdown summary for a cycle.

        This implements the karpathy pattern of creating summary artifacts
        that compress multiple task outputs into a human-readable form.

        Args:
            cycle: Cycle number

        Returns:
            Markdown summary text
        """
        cycle_dir = self.get_cycle_dir(cycle)
        findings = self.get_all_cycle_findings(cycle)

        # Build summary
        summary = f"# Cycle {cycle} Summary\n\n"
        summary += f"**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"**Findings**: {len(findings)}\n\n"

        # Statistics
        p_values = [
            f["statistics"].get("p_value")
            for f in findings
            if f["statistics"].get("p_value") is not None
        ]

        if p_values:
            significant = sum(1 for p in p_values if p < 0.05)
            summary += f"**Significant results (p < 0.05)**: {significant}/{len(p_values)}\n\n"

        # Key findings
        summary += "## Key Findings\n\n"
        for i, finding in enumerate(findings, 1):
            summary += f"### Task {finding['task']}: {finding['finding_id']}\n\n"
            summary += f"{finding['summary']}\n\n"

            stats = finding.get("statistics", {})
            if stats.get("p_value") is not None:
                summary += f"- **p-value**: {stats['p_value']:.2e}\n"
            if stats.get("confidence") is not None:
                summary += f"- **Confidence**: {stats['confidence']:.0%}\n"
            if stats.get("fold_change") is not None:
                summary += f"- **Fold change**: {stats['fold_change']:.2f}\n"

            summary += f"- **Notebook**: {finding['notebook_path']}\n\n"

        # Save summary artifact
        summary_path = cycle_dir / f"cycle_{cycle}_summary.md"
        with open(summary_path, "w") as f:
            f.write(summary)

        logger.info(f"Generated cycle summary: {summary_path}")

        return summary

    async def generate_final_synthesis(
        self,
        total_cycles: int,
        research_objective: str
    ) -> Path:
        """
        Generate final synthesis across all cycles.

        This is the top-level summary that compresses all cycle summaries
        into a final research report.

        Args:
            total_cycles: Total number of cycles completed
            research_objective: Original research objective

        Returns:
            Path to final synthesis document
        """
        synthesis = f"# Kosmos Research Synthesis\n\n"
        synthesis += f"**Research Objective**: {research_objective}\n\n"
        synthesis += f"**Cycles Completed**: {total_cycles}\n"
        synthesis += f"**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Aggregate statistics
        total_findings = 0
        all_p_values = []

        for cycle in range(1, total_cycles + 1):
            findings = self.get_all_cycle_findings(cycle)
            total_findings += len(findings)

            for finding in findings:
                p_value = finding.get("statistics", {}).get("p_value")
                if p_value is not None:
                    all_p_values.append(p_value)

        synthesis += f"**Total Findings**: {total_findings}\n"
        if all_p_values:
            significant = sum(1 for p in all_p_values if p < 0.05)
            synthesis += f"**Significant Results**: {significant}/{len(all_p_values)} ({significant/len(all_p_values):.0%})\n"
        synthesis += "\n"

        # Include cycle summaries
        synthesis += "## Discovery Timeline\n\n"

        for cycle in range(1, total_cycles + 1):
            cycle_dir = self.get_cycle_dir(cycle)
            summary_path = cycle_dir / f"cycle_{cycle}_summary.md"

            if summary_path.exists():
                synthesis += f"### Cycle {cycle}\n\n"
                with open(summary_path) as f:
                    # Skip the title line
                    lines = f.readlines()[1:]
                    synthesis += "".join(lines)
                synthesis += "\n---\n\n"

        # Save final synthesis
        final_path = self.sandbox / "final_synthesis.md"
        with open(final_path, "w") as f:
            f.write(synthesis)

        logger.info(f"Generated final synthesis: {final_path}")

        return final_path

    def get_artifact_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about artifacts.

        Returns:
            Dict with artifact statistics
        """
        cycles = list(self.sandbox.glob("cycle_*"))

        total_findings = 0
        total_summaries = 0

        for cycle_dir in cycles:
            findings = list(cycle_dir.glob("task_*_finding.json"))
            total_findings += len(findings)

            summaries = list(cycle_dir.glob("cycle_*_summary.md"))
            total_summaries += len(summaries)

        return {
            "sandbox_dir": str(self.sandbox),
            "total_cycles": len(cycles),
            "total_findings": total_findings,
            "total_cycle_summaries": total_summaries,
            "has_final_synthesis": (self.sandbox / "final_synthesis.md").exists(),
            "storage_size_mb": sum(
                f.stat().st_size for f in self.sandbox.rglob("*") if f.is_file()
            ) / (1024 * 1024)
        }
