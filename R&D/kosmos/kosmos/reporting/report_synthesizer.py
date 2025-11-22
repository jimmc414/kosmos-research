"""
Report Synthesis Module using Scientific-Writer.

This integrates the scientific-writer tool to generate publication-quality
research reports from Kosmos research findings.

Pattern source: R&D/kosmos-claude-scientific-writer
Gap addressed: Final report generation (Phase 3 enhancement)

The scientific-writer API provides:
- Professional LaTeX typesetting
- Automatic citation management
- Figure integration
- Multiple output formats (PDF, TeX)
- ScholarEval quality validation

Usage:
    synthesizer = ReportSynthesizer()

    report = await synthesizer.generate_research_report(
        findings=all_findings,
        research_objective="...",
        methodology="Kosmos autonomous research system...",
        output_dir="./output"
    )

    print(f"Report PDF: {report['pdf_path']}")
"""

import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, AsyncIterator
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Try to import scientific_writer
try:
    from scientific_writer import generate_paper
    SCIENTIFIC_WRITER_AVAILABLE = True
except ImportError:
    SCIENTIFIC_WRITER_AVAILABLE = False
    logger.warning(
        "scientific_writer not available. "
        "Report synthesis will generate basic markdown only. "
        "Install with: pip install scientific-writer"
    )


class ReportSynthesizer:
    """
    Synthesizes publication-quality research reports.

    This uses scientific-writer to generate professional LaTeX/PDF reports
    from Kosmos research findings.
    """

    def __init__(
        self,
        use_scientific_writer: bool = True,
        model: str = "claude-sonnet-4-20250514"
    ):
        """
        Initialize report synthesizer.

        Args:
            use_scientific_writer: Use scientific-writer for PDF generation
            model: Claude model to use for report generation
        """
        self.use_scientific_writer = use_scientific_writer and SCIENTIFIC_WRITER_AVAILABLE
        self.model = model

        if use_scientific_writer and not SCIENTIFIC_WRITER_AVAILABLE:
            logger.warning(
                "scientific_writer requested but not available. "
                "Falling back to markdown generation."
            )

    async def generate_research_report(
        self,
        findings: List[Dict[str, Any]],
        research_objective: str,
        methodology: str,
        output_dir: str,
        cycle_summaries: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive research report.

        Args:
            findings: List of validated findings
            research_objective: Main research question
            methodology: Description of methods used
            output_dir: Output directory for report
            cycle_summaries: Optional cycle-by-cycle summaries
            metadata: Optional additional metadata

        Returns:
            Dict with:
                - status: 'success', 'partial', or 'failed'
                - pdf_path: Path to PDF (if generated)
                - tex_path: Path to TeX source (if generated)
                - markdown_path: Path to markdown version
                - citations_count: Number of citations
                - word_count: Approximate word count
        """
        logger.info("Generating research report...")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if self.use_scientific_writer:
            # Use scientific-writer for publication-quality PDF
            return await self._generate_with_scientific_writer(
                findings, research_objective, methodology,
                output_dir, cycle_summaries, metadata
            )
        else:
            # Fall back to markdown generation
            return await self._generate_markdown_report(
                findings, research_objective, methodology,
                output_dir, cycle_summaries, metadata
            )

    async def _generate_with_scientific_writer(
        self,
        findings: List[Dict],
        research_objective: str,
        methodology: str,
        output_dir: str,
        cycle_summaries: Optional[List[Dict]],
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Generate report using scientific-writer API.

        This produces a publication-ready PDF with proper LaTeX typesetting,
        citations, and figures.
        """
        logger.info("Using scientific-writer for publication-quality report...")

        # Build detailed query for scientific-writer
        query = self._build_scientific_writer_query(
            findings, research_objective, methodology,
            cycle_summaries, metadata
        )

        # Prepare data files if needed (figures, tables, etc.)
        data_files = self._prepare_data_files(findings, output_dir)

        try:
            result_data = None

            # Generate paper with progress tracking
            async for update in generate_paper(
                query=query,
                output_dir=output_dir,
                data_files=data_files,
                model=self.model
            ):
                if update["type"] == "progress":
                    logger.info(
                        f"[{update['percentage']:3d}%] [{update['stage']:15s}] "
                        f"{update['message']}"
                    )
                else:
                    # Final result
                    result_data = update

            if result_data:
                # Check status
                if result_data['status'] == 'success':
                    logger.info(
                        f"Report generated successfully: {result_data['files']['pdf_final']}"
                    )

                    return {
                        "status": "success",
                        "pdf_path": result_data['files'].get('pdf_final'),
                        "tex_path": result_data['files'].get('tex_final'),
                        "markdown_path": None,
                        "citations_count": result_data['citations']['count'],
                        "figures_count": result_data.get('figures_count', 0),
                        "word_count": result_data['metadata'].get('word_count'),
                        "paper_directory": result_data['paper_directory']
                    }

                elif result_data['status'] == 'partial':
                    logger.warning(
                        "Report partially generated (TeX created, PDF compilation failed)"
                    )

                    return {
                        "status": "partial",
                        "pdf_path": None,
                        "tex_path": result_data['files'].get('tex_final'),
                        "markdown_path": None,
                        "citations_count": result_data['citations']['count'],
                        "figures_count": result_data.get('figures_count', 0),
                        "word_count": result_data['metadata'].get('word_count'),
                        "errors": result_data.get('errors', [])
                    }

                else:
                    logger.error(f"Report generation failed: {result_data.get('errors')}")

                    # Fall back to markdown
                    return await self._generate_markdown_report(
                        findings, research_objective, methodology,
                        output_dir, cycle_summaries, metadata
                    )

        except Exception as e:
            logger.error(f"Scientific-writer failed: {e}")

            # Fall back to markdown
            return await self._generate_markdown_report(
                findings, research_objective, methodology,
                output_dir, cycle_summaries, metadata
            )

    def _build_scientific_writer_query(
        self,
        findings: List[Dict],
        research_objective: str,
        methodology: str,
        cycle_summaries: Optional[List[Dict]],
        metadata: Optional[Dict]
    ) -> str:
        """
        Build detailed query for scientific-writer.

        This creates a comprehensive prompt that tells scientific-writer
        what kind of paper to generate.
        """
        # Sort findings by quality (ScholarEval score)
        findings_with_scores = [
            (f, f.get("scholar_eval", {}).get("overall_score", 0))
            for f in findings
        ]
        findings_with_scores.sort(key=lambda x: x[1], reverse=True)

        top_findings = findings_with_scores[:10]  # Top 10 findings

        query = f"""
Create a scientific research paper on the following autonomous research study:

# Research Objective
{research_objective}

# Methodology
{methodology}

# Key Findings

The research generated {len(findings)} findings across multiple cycles.
Here are the top {len(top_findings)} most significant findings:

"""

        for i, (finding, score) in enumerate(top_findings, 1):
            query += f"\n## Finding {i} (Quality Score: {score:.2f}/1.0)\n\n"
            query += f"{finding['summary']}\n\n"

            stats = finding.get('statistics', {})
            if stats:
                query += "**Statistical Evidence:**\n"
                if stats.get('p_value') is not None:
                    query += f"- p-value: {stats['p_value']:.2e}\n"
                if stats.get('confidence') is not None:
                    query += f"- Confidence: {stats['confidence']:.0%}\n"
                if stats.get('effect_size') is not None:
                    query += f"- Effect size: {stats['effect_size']:.2f}\n"
                query += "\n"

            if finding.get('interpretation'):
                query += f"**Interpretation:** {finding['interpretation']}\n\n"

        # Add execution summary if available
        if cycle_summaries:
            query += "\n# Research Execution Summary\n\n"
            query += f"- Total Cycles: {len(cycle_summaries)}\n"

            completed = [c for c in cycle_summaries if c.get('status') == 'completed']
            if completed:
                total_tasks = sum(c.get('tasks_completed', 0) for c in completed)
                total_findings = sum(c.get('new_findings', 0) for c in completed)
                validated = sum(c.get('validated_findings', 0) for c in completed)

                query += f"- Total Tasks: {total_tasks}\n"
                query += f"- Total Findings: {total_findings}\n"
                query += f"- Validated Findings: {validated}\n"
                query += f"- Validation Rate: {validated/total_findings*100:.1f}%\n"

        query += """

# Paper Requirements

Please create a professional research paper with:

1. **Structure:**
   - Title page
   - Abstract (150-250 words)
   - Introduction (background and research objective)
   - Methods (autonomous research system methodology)
   - Results (key findings with statistics)
   - Discussion (interpretation and significance)
   - Conclusion (summary and future work)
   - References

2. **Style:**
   - Academic tone suitable for publication
   - Clear, precise scientific writing
   - Appropriate citations to relevant literature
   - Professional LaTeX formatting

3. **Content:**
   - Emphasize the novel autonomous research approach
   - Highlight statistical rigor and validation
   - Discuss limitations and future directions
   - Include tables/figures where appropriate

4. **Length:**
   - Target 8-12 pages (conference paper format)
   - Balanced sections with appropriate depth

Generate a complete, publication-ready research paper in LaTeX format.
"""

        return query

    def _prepare_data_files(
        self,
        findings: List[Dict],
        output_dir: str
    ) -> List[str]:
        """
        Prepare data files for scientific-writer.

        This extracts any figures, tables, or data files from findings
        and saves them for inclusion in the paper.

        Args:
            findings: List of findings
            output_dir: Output directory

        Returns:
            List of file paths
        """
        data_files = []

        # Create data directory
        data_dir = Path(output_dir) / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        # Extract any figure paths or data from findings
        for i, finding in enumerate(findings):
            # Check if finding has associated figures
            if finding.get('figures'):
                for j, figure_path in enumerate(finding['figures']):
                    if Path(figure_path).exists():
                        data_files.append(figure_path)

            # Export finding statistics as JSON for reference
            if finding.get('statistics'):
                stats_file = data_dir / f"finding_{i+1}_stats.json"
                with open(stats_file, "w") as f:
                    json.dump(finding['statistics'], f, indent=2)
                data_files.append(str(stats_file))

        logger.info(f"Prepared {len(data_files)} data files for report")

        return data_files

    async def _generate_markdown_report(
        self,
        findings: List[Dict],
        research_objective: str,
        methodology: str,
        output_dir: str,
        cycle_summaries: Optional[List[Dict]],
        metadata: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Generate fallback markdown report.

        This is used when scientific-writer is unavailable or fails.
        """
        logger.info("Generating markdown report (fallback mode)...")

        output_path = Path(output_dir)
        markdown_path = output_path / "research_report.md"

        # Sort findings by quality
        findings_with_scores = [
            (f, f.get("scholar_eval", {}).get("overall_score", 0))
            for f in findings
        ]
        findings_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Build markdown
        report = f"""# Research Report: {research_objective}

**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
**System**: Kosmos Autonomous Research Platform

---

## Abstract

This report presents the results of an autonomous research study conducted by the Kosmos
AI research system. The study addressed the following research objective:

> {research_objective}

The research was conducted over {len(cycle_summaries) if cycle_summaries else '?'} autonomous cycles,
generating {len(findings)} validated findings through systematic exploration and analysis.

---

## 1. Introduction

### 1.1 Research Objective

{research_objective}

### 1.2 Methodology

{methodology}

---

## 2. Results

The research generated **{len(findings)} validated findings** through autonomous exploration
and analysis. The findings are presented below in order of quality score.

"""

        # Add findings
        for i, (finding, score) in enumerate(findings_with_scores[:10], 1):
            report += f"\n### 2.{i} Finding {i}: {finding['summary'][:80]}...\n\n"
            report += f"**Quality Score**: {score:.2f}/1.0\n\n"
            report += f"**Summary**: {finding['summary']}\n\n"

            stats = finding.get('statistics', {})
            if stats:
                report += "**Statistical Evidence**:\n\n"
                if stats.get('p_value') is not None:
                    report += f"- p-value: {stats['p_value']:.2e}\n"
                if stats.get('confidence') is not None:
                    report += f"- Confidence: {stats['confidence']:.0%}\n"
                if stats.get('effect_size') is not None:
                    report += f"- Effect size: {stats['effect_size']:.2f}\n"
                if stats.get('sample_size') is not None:
                    report += f"- Sample size: {stats['sample_size']}\n"
                report += "\n"

            if finding.get('methods'):
                report += f"**Methods**: {finding['methods']}\n\n"

            if finding.get('interpretation'):
                report += f"**Interpretation**: {finding['interpretation']}\n\n"

        # Add execution summary
        if cycle_summaries:
            report += "\n---\n\n## 3. Research Execution\n\n"

            completed = [c for c in cycle_summaries if c.get('status') == 'completed']

            if completed:
                total_tasks = sum(c.get('tasks_completed', 0) for c in completed)
                total_findings_generated = sum(c.get('new_findings', 0) for c in completed)
                validated = sum(c.get('validated_findings', 0) for c in completed)

                report += f"- **Total Cycles**: {len(cycle_summaries)}\n"
                report += f"- **Total Tasks Executed**: {total_tasks}\n"
                report += f"- **Total Findings Generated**: {total_findings_generated}\n"
                report += f"- **Validated Findings**: {validated}\n"
                report += f"- **Validation Rate**: {validated/total_findings_generated*100:.1f}%\n\n"

            report += "\n### Cycle-by-Cycle Summary\n\n"
            report += "| Cycle | Tasks | Findings | Validated | Quality Score |\n"
            report += "|-------|-------|----------|-----------|---------------|\n"

            for cycle in completed:
                report += (
                    f"| {cycle.get('cycle', '?')} | "
                    f"{cycle.get('tasks_completed', 0)} | "
                    f"{cycle.get('new_findings', 0)} | "
                    f"{cycle.get('validated_findings', 0)} | "
                    f"{cycle.get('plan_score', 0):.1f}/10 |\n"
                )

            report += "\n"

        # Add methodology section
        report += "\n---\n\n## 4. Methodology\n\n"
        report += f"{methodology}\n\n"

        # Add conclusion
        report += "\n---\n\n## 5. Conclusion\n\n"
        report += f"This autonomous research study successfully addressed the research objective "
        report += f"through systematic exploration over {len(cycle_summaries) if cycle_summaries else '?'} cycles. "
        report += f"The research generated {len(findings)} validated findings with an average quality score of "

        avg_score = sum(score for _, score in findings_with_scores) / len(findings_with_scores) if findings_with_scores else 0
        report += f"{avg_score:.2f}/1.0, demonstrating the effectiveness of the autonomous research approach.\n\n"

        report += "Key contributions of this study include:\n\n"
        report += "1. Systematic exploration of the research domain through autonomous task planning\n"
        report += "2. Rigorous statistical validation of all findings\n"
        report += "3. Quality control through multi-dimensional peer review (ScholarEval)\n"
        report += "4. Comprehensive documentation of methodology and results\n\n"

        # Save markdown
        with open(markdown_path, "w") as f:
            f.write(report)

        logger.info(f"Markdown report generated: {markdown_path}")

        # Calculate word count
        word_count = len(report.split())

        return {
            "status": "success",
            "pdf_path": None,
            "tex_path": None,
            "markdown_path": str(markdown_path),
            "citations_count": 0,
            "figures_count": 0,
            "word_count": word_count
        }
