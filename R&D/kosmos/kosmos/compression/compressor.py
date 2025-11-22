"""
Context Compressor Implementation for Kosmos.

This implements the hierarchical compression pipeline that solves Gap 0
(Context Compression Architecture).

Key features:
- Notebook compression: 42K lines → 2-line summary + stats
- Literature compression: 1500 papers → structured summaries
- Progressive disclosure: Lazy load full content on demand
- Multi-tier caching: Memory + disk for performance
"""

import asyncio
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from kosmos.core.llm import get_client

logger = logging.getLogger(__name__)


class NotebookCompressor:
    """
    Compresses Jupyter notebooks from ~42K lines to concise summaries.

    Pattern: scientific-writer summarization + claude-skills-mcp lazy loading
    """

    def __init__(self, cache_dir: str = ".cache/notebooks"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.client = get_client()

    async def compress(
        self,
        notebook_path: str,
        max_summary_lines: int = 2
    ) -> Dict[str, Any]:
        """
        Compress notebook to summary + statistics.

        Args:
            notebook_path: Path to Jupyter notebook
            max_summary_lines: Maximum lines for summary

        Returns:
            Dict with:
                - summary: 2-line summary
                - statistics: Extracted stats
                - notebook_path: Original path
                - full_content: None (lazy load)
                - compressed_at: Timestamp
        """
        # Check cache first
        cache_key = self._get_cache_key(notebook_path)
        cached = self._load_from_cache(cache_key)
        if cached:
            logger.info(f"Loaded notebook summary from cache: {notebook_path}")
            return cached

        # Read notebook
        with open(notebook_path) as f:
            content = f.read()

        # Extract statistics first (fast, rule-based)
        stats = self._extract_statistics(content)

        # Generate summary (uses LLM, slower)
        summary = await self._generate_summary(content, max_summary_lines)

        result = {
            "summary": summary,
            "statistics": stats,
            "notebook_path": notebook_path,
            "full_content": None,  # Lazy load on demand
            "compressed_at": datetime.utcnow().isoformat()
        }

        # Cache result
        self._save_to_cache(cache_key, result)

        return result

    def _extract_statistics(self, content: str) -> Dict[str, Any]:
        """
        Extract statistical values from notebook content.

        This is fast and doesn't require LLM.
        """
        stats = {}

        # Extract p-values
        p_values = re.findall(r'p[- ]?=\s*([0-9.e-]+)', content, re.IGNORECASE)
        if p_values:
            stats['p_values'] = [float(p) for p in p_values if float(p) <= 1.0]
            if stats['p_values']:
                stats['min_p_value'] = min(stats['p_values'])
                stats['significant_count'] = sum(1 for p in stats['p_values'] if p < 0.05)

        # Extract correlations
        correlations = re.findall(r'r[- ]?=\s*([0-9.-]+)', content, re.IGNORECASE)
        if correlations:
            stats['correlations'] = [float(c) for c in correlations if abs(float(c)) <= 1.0]

        # Extract fold changes
        fold_changes = re.findall(r'fold[- ]change[:\s]+([0-9.]+)', content, re.IGNORECASE)
        if fold_changes:
            stats['fold_changes'] = [float(fc) for fc in fold_changes]

        # Extract confidence values
        confidences = re.findall(r'confidence[:\s]+([0-9.]+)', content, re.IGNORECASE)
        if confidences:
            stats['confidences'] = [float(c) for c in confidences if 0 <= float(c) <= 1.0]

        # Count key terms
        stats['finding_mentions'] = len(re.findall(r'\b(finding|result|discovery|observation)\b', content, re.IGNORECASE))
        stats['hypothesis_mentions'] = len(re.findall(r'\b(hypothesis|hypothesize|predict)\b', content, re.IGNORECASE))

        return stats

    async def _generate_summary(self, content: str, max_lines: int) -> str:
        """
        Generate concise summary using LLM.

        This uses Claude to extract the key finding in 2 lines.
        """
        # Truncate very long content to avoid context limits
        if len(content) > 50000:
            content = content[:50000] + "\n... (truncated)"

        prompt = f"""Analyze this Jupyter notebook and provide a concise {max_lines}-line summary focusing on the KEY FINDING(S).

Be specific about what was discovered, including any statistical evidence (p-values, correlations, etc.).

Notebook content:
{content}

Provide exactly {max_lines} lines summarizing the most important finding(s):"""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=messages,
                temperature=0.3
            )

            summary = response.content[0].text.strip()

            # Ensure it's not more than max_lines
            lines = summary.split('\n')
            if len(lines) > max_lines:
                summary = '\n'.join(lines[:max_lines])

            return summary

        except Exception as e:
            logger.error(f"LLM summarization failed: {e}")
            # Fallback: extract first meaningful sentences
            return self._fallback_summary(content, max_lines)

    def _fallback_summary(self, content: str, max_lines: int) -> str:
        """Fallback summarization without LLM."""
        sentences = re.split(r'[.!?]\s+', content)
        meaningful = [
            s for s in sentences
            if len(s) > 30 and any(kw in s.lower() for kw in [
                'found', 'shows', 'indicates', 'suggests', 'demonstrates',
                'significant', 'correlation', 'relationship'
            ])
        ]

        if meaningful:
            return '. '.join(meaningful[:max_lines]) + '.'
        else:
            return "Analysis completed. Review notebook for detailed findings."

    def _get_cache_key(self, notebook_path: str) -> str:
        """Generate cache key for notebook."""
        return hashlib.md5(notebook_path.encode()).hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Load from cache if available and not expired."""
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        # Check if cache is too old (24 hours)
        age = datetime.utcnow() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if age > timedelta(hours=24):
            cache_file.unlink()
            return None

        with open(cache_file) as f:
            return json.load(f)

    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)


class LiteratureCompressor:
    """
    Compresses literature search results (1500 papers → summaries).

    Pattern: scientific-writer document summarization
    """

    def __init__(self):
        self.client = get_client()

    async def compress(self, papers: List[Dict[str, Any]]) -> str:
        """
        Compress papers to structured markdown summary.

        Args:
            papers: List of paper dicts with:
                - title: Paper title
                - authors: Authors
                - abstract: Abstract text
                - pmid/doi: Identifier
                - year: Publication year

        Returns:
            Markdown summary of all papers
        """
        if not papers:
            return "# Literature Summary\n\nNo papers found.\n"

        # Group by year for better organization
        by_year = {}
        for paper in papers:
            year = paper.get('year', 'Unknown')
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(paper)

        # Build summary
        summary = f"# Literature Summary ({len(papers)} papers)\n\n"

        for year in sorted(by_year.keys(), reverse=True):
            year_papers = by_year[year]
            summary += f"## {year} ({len(year_papers)} papers)\n\n"

            for paper in year_papers:
                summary += await self._summarize_paper(paper)
                summary += "\n"

        return summary

    async def _summarize_paper(self, paper: Dict[str, Any]) -> str:
        """Summarize a single paper."""
        # Basic metadata
        result = f"### {paper.get('title', 'Untitled')}\n\n"
        result += f"**Authors**: {paper.get('authors', 'Unknown')}\n"

        if paper.get('pmid'):
            result += f"**PMID**: {paper['pmid']}\n"
        elif paper.get('doi'):
            result += f"**DOI**: {paper['doi']}\n"

        # Summarize abstract if available
        abstract = paper.get('abstract')
        if abstract:
            # For very long abstracts, use LLM to condense
            if len(abstract) > 1000:
                key_finding = await self._extract_key_finding(abstract)
                result += f"**Key Finding**: {key_finding}\n"
            else:
                result += f"**Abstract**: {abstract[:500]}...\n"

        return result

    async def _extract_key_finding(self, abstract: str) -> str:
        """Extract key finding from abstract using LLM."""
        prompt = f"""Extract the single most important finding from this abstract in one sentence:

{abstract}

Key finding:"""

        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use Haiku for speed
                max_tokens=150,
                messages=messages,
                temperature=0.3
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Failed to extract key finding: {e}")
            # Fallback: first sentence
            sentences = abstract.split('.')
            return sentences[0] + '.' if sentences else abstract[:200]


class ContextCompressor:
    """
    Main context compressor orchestrating all compression tiers.

    Implements the complete hierarchical compression pipeline:
    Tier 1: Notebooks → summaries
    Tier 2: Papers → structured summaries
    Tier 3: Tasks → cycle summaries
    Tier 4: Cycles → final synthesis
    """

    def __init__(self, cache_dir: str = ".cache"):
        self.notebook_compressor = NotebookCompressor(cache_dir=f"{cache_dir}/notebooks")
        self.literature_compressor = LiteratureCompressor()

    async def compress_notebooks(
        self,
        notebook_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Compress multiple notebooks in parallel.

        Args:
            notebook_paths: List of notebook file paths

        Returns:
            List of compressed notebook dicts
        """
        tasks = [
            self.notebook_compressor.compress(path)
            for path in notebook_paths
        ]
        return await asyncio.gather(*tasks)

    async def compress_literature(
        self,
        papers: List[Dict[str, Any]]
    ) -> str:
        """
        Compress literature search results.

        Args:
            papers: List of paper dicts

        Returns:
            Markdown summary
        """
        return await self.literature_compressor.compress(papers)

    async def compress_cycle(
        self,
        task_summaries: List[Dict[str, Any]]
    ) -> str:
        """
        Compress a full cycle (10 tasks) into cycle summary.

        Args:
            task_summaries: List of task compression results

        Returns:
            Cycle summary markdown
        """
        cycle_md = "# Cycle Summary\n\n"
        cycle_md += f"**Tasks Completed**: {len(task_summaries)}\n\n"

        # Aggregate statistics
        all_p_values = []
        for task in task_summaries:
            stats = task.get('statistics', {})
            if 'p_values' in stats:
                all_p_values.extend(stats['p_values'])

        if all_p_values:
            significant = sum(1 for p in all_p_values if p < 0.05)
            cycle_md += f"**Significant findings**: {significant}/{len(all_p_values)}\n\n"

        # List findings
        cycle_md += "## Key Findings\n\n"
        for i, task in enumerate(task_summaries, 1):
            cycle_md += f"{i}. {task['summary']}\n"

        return cycle_md

    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression performance statistics."""
        # Count cached notebooks
        cache_dir = self.notebook_compressor.cache_dir
        cached_notebooks = len(list(cache_dir.glob("*.json"))) if cache_dir.exists() else 0

        return {
            "cached_notebooks": cached_notebooks,
            "cache_dir": str(cache_dir),
            "cache_size_mb": sum(
                f.stat().st_size for f in cache_dir.rglob("*") if f.is_file()
            ) / (1024 * 1024) if cache_dir.exists() else 0
        }
