"""
Reporting Module for Kosmos.

This module provides publication-quality report synthesis using scientific-writer
for generating professional research papers from Kosmos findings.

Pattern source: R&D/kosmos-claude-scientific-writer
Gap addressed: Final report generation (Phase 3 enhancement)

Key components:
- ReportSynthesizer: Generates publication-ready reports
- scientific-writer integration: Professional LaTeX/PDF generation
- Markdown fallback: Basic reports when scientific-writer unavailable

Usage:
    from kosmos.reporting import ReportSynthesizer

    synthesizer = ReportSynthesizer(use_scientific_writer=True)

    report = await synthesizer.generate_research_report(
        findings=validated_findings,
        research_objective="...",
        methodology="Kosmos autonomous research system...",
        output_dir="./output"
    )

    if report['pdf_path']:
        print(f"PDF report: {report['pdf_path']}")
    else:
        print(f"Markdown report: {report['markdown_path']}")
"""

from .report_synthesizer import ReportSynthesizer

__all__ = ["ReportSynthesizer"]
