"""
Context Compression Pipeline Demo for Kosmos

Demonstrates hierarchical compression using patterns from:
- scientific-writer (document summarization)
- claude-skills-mcp (progressive disclosure, lazy loading)
- karpathy (artifact-based communication)

This solves Gap 0 (Context Compression Architecture) by showing how to:
1. Compress notebooks (42K lines → 2-line summary + stats)
2. Compress papers (1500 papers → structured summaries)
3. Compress cycles (10 tasks → cycle summary)
4. Generate final synthesis (20 cycles → research report)
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List
import re


class ContextCompressor:
    """
    Multi-tier context compression for Kosmos

    Tier 1: Task-level (notebook → summary)
    Tier 2: Literature (papers → structured summaries)
    Tier 3: Cycle-level (10 tasks → cycle summary)
    Tier 4: Final synthesis (20 cycles → report)
    """

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    async def compress_notebook(self, notebook_path: str) -> Dict:
        """
        Task-level compression: 42K lines → 2-line summary + stats

        This demonstrates:
        - Lazy loading (don't load full notebook upfront)
        - Statistics extraction
        - LLM summarization
        """
        # Read notebook (in production, this would be lazy)
        with open(notebook_path) as f:
            content = f.read()

        # Extract key statistics
        stats = self._extract_stats(content)

        # Generate 2-line summary (would use Claude in production)
        summary = self._mock_summarize(content, max_lines=2)

        # Cache result
        cache_key = Path(notebook_path).stem
        cached = {
            "summary": summary,
            "statistics": stats,
            "notebook_path": notebook_path,
            "full_content": None,  # Lazy load on demand
            "compressed_at": "2025-11-22T10:00:00"
        }

        cache_file = self.cache_dir / f"{cache_key}_compressed.json"
        with open(cache_file, "w") as f:
            json.dump(cached, f, indent=2)

        return cached

    def _extract_stats(self, notebook_content: str) -> Dict:
        """
        Extract p-values, correlations, effect sizes from notebook

        Pattern from: Kosmos paper (Section 2.3)
        """
        stats = {}

        # Extract p-values
        p_values = re.findall(r'p[- ]?=\s*([0-9.e-]+)', notebook_content)
        if p_values:
            stats['p_values'] = [float(p) for p in p_values]
            stats['min_p_value'] = min(stats['p_values'])

        # Extract correlation coefficients
        correlations = re.findall(r'r[- ]?=\s*([0-9.-]+)', notebook_content)
        if correlations:
            stats['correlations'] = [float(c) for c in correlations]

        # Extract fold changes
        fold_changes = re.findall(r'fold[- ]change[: ]+([0-9.]+)', notebook_content, re.IGNORECASE)
        if fold_changes:
            stats['fold_changes'] = [float(fc) for fc in fold_changes]

        # Count findings
        stats['num_findings'] = len(re.findall(r'finding|result|discovery', notebook_content, re.IGNORECASE))

        return stats

    def _mock_summarize(self, content: str, max_lines: int = 2) -> str:
        """
        Mock LLM summarization (would use Claude in production)

        In production, this would call:
        - Anthropic Claude Sonnet 4.5 with scientific-skills context
        - Prompt: "Summarize this analysis in 2 lines focusing on key findings"
        """
        # Simple mock: extract first meaningful sentences
        sentences = re.split(r'[.!?]\s+', content)
        meaningful = [s for s in sentences if len(s) > 50 and any(kw in s.lower() for kw in ['found', 'shows', 'indicates', 'suggests', 'demonstrates'])]

        if len(meaningful) >= max_lines:
            return '. '.join(meaningful[:max_lines]) + '.'
        else:
            return '. '.join(sentences[:max_lines]) + '.' if sentences else "Analysis completed with findings."

    async def compress_papers(self, papers: List[Dict]) -> str:
        """
        Literature compression: 1500 papers → structured summary

        Pattern from: scientific-writer document summarization
        """
        summaries = []

        for paper in papers:
            # In production: use scientific-writer's summarization
            # from scientific_writer import summarize_paper
            # summary = await summarize_paper(paper['content'])

            summary = {
                'title': paper['title'],
                'authors': paper['authors'],
                'key_finding': self._mock_summarize(paper['abstract'], max_lines=1),
                'methods': paper.get('methods', 'Not available'),
                'pmid': paper.get('pmid', 'Unknown')
            }
            summaries.append(summary)

        # Combine into structured markdown
        combined = f"# Literature Summary ({len(papers)} papers)\n\n"
        for i, s in enumerate(summaries, 1):
            combined += f"## {i}. {s['title']}\n"
            combined += f"**Authors**: {s['authors']}\n"
            combined += f"**Finding**: {s['key_finding']}\n"
            combined += f"**PMID**: {s['pmid']}\n\n"

        return combined

    async def compress_cycle(self, cycle_findings: List[Dict]) -> str:
        """
        Cycle-level: 10 task summaries → cycle summary

        Pattern from: karpathy artifact-based communication
        """
        # Aggregate findings
        all_summaries = [f["summary"] for f in cycle_findings]
        all_stats = [f["statistics"] for f in cycle_findings]

        # Generate cycle-level insights
        cycle_summary = f"# Cycle Summary\n\n"
        cycle_summary += f"**Tasks Completed**: {len(cycle_findings)}\n\n"

        cycle_summary += "## Key Findings\n\n"
        for i, finding in enumerate(cycle_findings, 1):
            cycle_summary += f"{i}. {finding['summary']}\n"

        # Aggregate statistics
        cycle_summary += "\n## Aggregate Statistics\n\n"
        all_p_values = []
        for stat in all_stats:
            if 'p_values' in stat:
                all_p_values.extend(stat['p_values'])

        if all_p_values:
            cycle_summary += f"- Total significant findings (p < 0.05): {sum(1 for p in all_p_values if p < 0.05)}\n"
            cycle_summary += f"- Minimum p-value: {min(all_p_values):.2e}\n"

        return cycle_summary

    async def generate_final_synthesis(self, all_cycle_summaries: List[str]) -> Dict:
        """
        Final synthesis: 20 cycle summaries → research report

        In production: Use scientific-writer's full capabilities
        from scientific_writer import generate_paper

        async for update in generate_paper(query):
            if update["type"] == "result":
                return update["files"]
        """
        # Mock final report
        report = "# Kosmos Discovery Report\n\n"
        report += f"## Executive Summary\n\n"
        report += f"This report synthesizes {len(all_cycle_summaries)} cycles of autonomous research.\n\n"

        for i, cycle_summary in enumerate(all_cycle_summaries, 1):
            report += f"\n## Cycle {i}\n\n"
            report += cycle_summary + "\n"

        # Save to file
        report_path = self.cache_dir / "final_synthesis.md"
        with open(report_path, "w") as f:
            f.write(report)

        return {
            "markdown": str(report_path),
            "pdf": str(report_path.with_suffix('.pdf')),  # Would be generated in production
            "word": str(report_path.with_suffix('.docx'))
        }


async def demo():
    """Demonstrate context compression pipeline"""
    compressor = ContextCompressor(cache_dir=".cache_demo")

    print("=" * 80)
    print("CONTEXT COMPRESSION PIPELINE DEMO")
    print("=" * 80)
    print()

    # Create mock notebook content
    mock_notebook = """
    # Single-Cell RNA-seq Analysis

    ## Methods
    We analyzed 10,000 cells using Scanpy.

    ## Results
    We found that gene BRCA1 is significantly upregulated in cancer cells (p = 0.001, fold change = 2.5).
    The correlation between BRCA1 and TP53 expression is r = 0.85.
    This suggests a strong regulatory relationship between these tumor suppressors.

    ## Conclusions
    Our analysis demonstrates that BRCA1 upregulation is a key feature of the cancer phenotype.
    """

    # Save mock notebook
    notebook_path = compressor.cache_dir / "mock_analysis.ipynb"
    with open(notebook_path, "w") as f:
        f.write(mock_notebook)

    # 1. Task-level compression
    print("1. TASK-LEVEL COMPRESSION (Notebook → Summary)")
    print("-" * 80)
    compressed_task = await compressor.compress_notebook(str(notebook_path))
    print(f"Original: {len(mock_notebook)} characters")
    print(f"Compressed: {len(compressed_task['summary'])} characters")
    print(f"\nSummary: {compressed_task['summary']}")
    print(f"Statistics: {json.dumps(compressed_task['statistics'], indent=2)}")
    print()

    # 2. Literature compression
    print("2. LITERATURE COMPRESSION (Papers → Summaries)")
    print("-" * 80)
    mock_papers = [
        {
            "title": "CRISPR-Cas9 in Cancer Therapy",
            "authors": "Smith et al.",
            "abstract": "We found that CRISPR editing of BRCA1 significantly reduces tumor growth in mouse models.",
            "pmid": "12345678"
        },
        {
            "title": "TP53 and BRCA1 Interaction Networks",
            "authors": "Jones et al.",
            "abstract": "Our study shows that TP53 and BRCA1 form a critical regulatory network in DNA repair.",
            "pmid": "23456789"
        }
    ]
    literature_summary = await compressor.compress_papers(mock_papers)
    print(f"Compressed {len(mock_papers)} papers")
    print(f"\n{literature_summary[:500]}...\n")

    # 3. Cycle-level compression
    print("3. CYCLE-LEVEL COMPRESSION (10 Tasks → Cycle Summary)")
    print("-" * 80)

    # Simulate 10 tasks
    cycle_findings = [compressed_task] * 5  # Simulate 5 tasks (would be 10 in production)

    cycle_summary = await compressor.compress_cycle(cycle_findings)
    print(cycle_summary)
    print()

    # 4. Final synthesis
    print("4. FINAL SYNTHESIS (20 Cycles → Research Report)")
    print("-" * 80)

    # Simulate 3 cycles (would be 20 in production)
    all_cycles = [cycle_summary] * 3

    final_report = await compressor.generate_final_synthesis(all_cycles)
    print(f"Generated final report:")
    print(f"  - Markdown: {final_report['markdown']}")
    print(f"  - PDF: {final_report['pdf']} (mock)")
    print(f"  - Word: {final_report['word']} (mock)")
    print()

    print("=" * 80)
    print("COMPRESSION METRICS")
    print("=" * 80)
    print(f"Original notebook: ~42,000 lines (typical from paper)")
    print(f"Compressed to: 2-line summary + statistics")
    print(f"Compression ratio: ~99.99%")
    print(f"\nThis demonstrates how Kosmos can handle:")
    print(f"  - 1,500 papers → structured summaries")
    print(f"  - 166 notebooks (42K lines each) → 166 2-line summaries")
    print(f"  - 20 cycles → final research report")
    print()
    print("Pattern sources:")
    print("  - scientific-writer: Document summarization, synthesis")
    print("  - claude-skills-mcp: Progressive disclosure, lazy loading")
    print("  - karpathy: Artifact-based communication")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demo())
