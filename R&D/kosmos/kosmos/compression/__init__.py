"""
Context Compression Module for Kosmos.

This module implements hierarchical context compression to solve Gap 0
(Context Compression Architecture), enabling Kosmos to handle 1,500 papers
and 42,000 lines of code per run while staying within LLM context windows.

Pattern sources:
- scientific-writer: Document summarization
- claude-skills-mcp: Progressive disclosure, lazy loading
- karpathy: Artifact-based communication

Architecture:
- Tier 1: Task-level (notebook → 2-line summary + stats)
- Tier 2: Literature (papers → structured summaries)
- Tier 3: Cycle-level (10 tasks → cycle summary)
- Tier 4: Final synthesis (20 cycles → report)

Usage:
    from kosmos.compression import ContextCompressor

    compressor = ContextCompressor()

    # Compress notebook
    summary = await compressor.compress_notebook(notebook_path)

    # Compress papers
    lit_summary = await compressor.compress_papers(papers)

    # Generate cycle summary
    cycle_summary = await compressor.compress_cycle(findings)
"""

from .compressor import ContextCompressor, NotebookCompressor, LiteratureCompressor

__all__ = ["ContextCompressor", "NotebookCompressor", "LiteratureCompressor"]
