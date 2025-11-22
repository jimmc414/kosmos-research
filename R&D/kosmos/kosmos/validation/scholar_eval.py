"""
ScholarEval Validation Framework for Kosmos.

This module implements the ScholarEval peer review framework from scientific-writer
to validate discoveries and filter out low-quality findings.

Pattern source: R&D/kosmos-claude-scientific-writer (ScholarEval)
Gap addressed: Gap 5 (Discovery Evaluation & Filtering)

ScholarEval provides 8-dimension scoring for scientific quality:
1. Novelty: How new/original is the finding?
2. Rigor: How well-supported by data?
3. Clarity: How clearly presented?
4. Reproducibility: Can others replicate it?
5. Impact: Scientific/practical significance?
6. Coherence: Logically consistent?
7. Limitations: Are limitations acknowledged?
8. Ethics: Appropriate ethical considerations?

Usage:
    evaluator = ScholarEvalValidator()

    # Evaluate a finding
    score = await evaluator.evaluate_finding(finding)

    if score.overall_score >= 0.75:
        # Finding passes quality threshold
        await state_manager.add_finding(finding)
    else:
        logger.warning(f"Finding rejected: {score.feedback}")
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

from kosmos.core.llm import get_client

logger = logging.getLogger(__name__)


@dataclass
class ScholarEvalScore:
    """
    ScholarEval evaluation result.

    8-dimension scoring system for scientific quality.
    """

    # Dimension scores (0.0-1.0)
    novelty: float
    rigor: float
    clarity: float
    reproducibility: float
    impact: float
    coherence: float
    limitations: float
    ethics: float

    # Overall assessment
    overall_score: float
    passes_threshold: bool
    feedback: str

    # Metadata
    evaluated_at: datetime
    evaluator_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "novelty": self.novelty,
            "rigor": self.rigor,
            "clarity": self.clarity,
            "reproducibility": self.reproducibility,
            "impact": self.impact,
            "coherence": self.coherence,
            "limitations": self.limitations,
            "ethics": self.ethics,
            "overall_score": self.overall_score,
            "passes_threshold": self.passes_threshold,
            "feedback": self.feedback,
            "evaluated_at": self.evaluated_at.isoformat(),
            "evaluator_version": self.evaluator_version
        }


class ScholarEvalValidator:
    """
    Validator using ScholarEval framework for scientific quality assessment.

    This implements the peer review framework from scientific-writer,
    adapted for evaluating Kosmos discoveries before they're added to
    the State Manager.
    """

    def __init__(
        self,
        threshold: float = 0.75,
        min_rigor_score: float = 0.7,
        require_citations: bool = True
    ):
        """
        Initialize validator.

        Args:
            threshold: Overall score threshold for acceptance (0.0-1.0)
            min_rigor_score: Minimum rigor score required
            require_citations: Whether findings must have citations
        """
        self.threshold = threshold
        self.min_rigor_score = min_rigor_score
        self.require_citations = require_citations
        self.client = get_client()

    async def evaluate_finding(self, finding: Dict[str, Any]) -> ScholarEvalScore:
        """
        Evaluate a finding using ScholarEval framework.

        Args:
            finding: Finding dict with:
                - summary: 2-line summary
                - statistics: Dict with p_value, confidence, etc.
                - notebook_path: Path to analysis notebook
                - citations: List of supporting papers
                - methods_description: Optional methods description

        Returns:
            ScholarEvalScore with dimension scores and overall assessment
        """
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(finding)

        # Get LLM evaluation
        response = await self._query_llm(prompt)

        # Parse scores
        scores = self._parse_llm_response(response)

        # Calculate overall score (weighted average)
        overall = self._calculate_overall_score(scores)

        # Check thresholds
        passes = (
            overall >= self.threshold and
            scores.get("rigor", 0) >= self.min_rigor_score
        )

        # Generate feedback
        feedback = self._generate_feedback(scores, passes, finding)

        return ScholarEvalScore(
            novelty=scores.get("novelty", 0.5),
            rigor=scores.get("rigor", 0.5),
            clarity=scores.get("clarity", 0.5),
            reproducibility=scores.get("reproducibility", 0.5),
            impact=scores.get("impact", 0.5),
            coherence=scores.get("coherence", 0.5),
            limitations=scores.get("limitations", 0.5),
            ethics=scores.get("ethics", 0.5),
            overall_score=overall,
            passes_threshold=passes,
            feedback=feedback,
            evaluated_at=datetime.utcnow()
        )

    def _build_evaluation_prompt(self, finding: Dict[str, Any]) -> str:
        """Build ScholarEval evaluation prompt."""
        prompt = f"""You are a scientific peer reviewer using the ScholarEval framework to evaluate research findings.

Evaluate the following finding on 8 dimensions, each scored 0.0-1.0:

**Finding Summary:**
{finding.get('summary', 'No summary provided')}

**Statistical Evidence:**
"""

        stats = finding.get('statistics', {})
        if stats.get('p_value') is not None:
            prompt += f"- p-value: {stats['p_value']:.2e}\n"
        if stats.get('confidence') is not None:
            prompt += f"- Confidence: {stats['confidence']:.0%}\n"
        if stats.get('fold_change') is not None:
            prompt += f"- Fold change: {stats['fold_change']:.2f}\n"

        if finding.get('citations'):
            prompt += f"\n**Supporting Literature:** {len(finding['citations'])} citations\n"

        if finding.get('methods_description'):
            prompt += f"\n**Methods:**\n{finding['methods_description']}\n"

        prompt += """

Evaluate on these dimensions:

1. **Novelty** (0.0-1.0): How original is this finding? Is it building on existing knowledge or discovering something new?

2. **Rigor** (0.0-1.0): How well-supported is the finding by data? Are the statistical tests appropriate? Is the effect size meaningful?

3. **Clarity** (0.0-1.0): How clearly is the finding presented? Is it specific and unambiguous?

4. **Reproducibility** (0.0-1.0): Could another researcher reproduce this result? Are the methods clear?

5. **Impact** (0.0-1.0): What is the scientific or practical significance? Could this lead to new research or applications?

6. **Coherence** (0.0-1.0): Is the finding logically consistent? Does it align with prior knowledge or provide good explanation if not?

7. **Limitations** (0.0-1.0): Are limitations and caveats acknowledged? Is the claim strength appropriate?

8. **Ethics** (0.0-1.0): Are there appropriate ethical considerations? Is the research responsible?

Respond in JSON format:
{
    "novelty": <score>,
    "rigor": <score>,
    "clarity": <score>,
    "reproducibility": <score>,
    "impact": <score>,
    "coherence": <score>,
    "limitations": <score>,
    "ethics": <score>,
    "reasoning": {
        "novelty": "<brief justification>",
        "rigor": "<brief justification>",
        ...
    }
}
"""

        return prompt

    async def _query_llm(self, prompt: str) -> str:
        """Query LLM for evaluation."""
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=messages,
                temperature=0.3  # Lower temperature for consistency
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            # Return conservative default scores
            return '{"novelty": 0.5, "rigor": 0.5, "clarity": 0.5, "reproducibility": 0.5, "impact": 0.5, "coherence": 0.5, "limitations": 0.5, "ethics": 0.5}'

    def _parse_llm_response(self, response: str) -> Dict[str, float]:
        """Parse LLM response to extract scores."""
        import json

        try:
            # Try to parse as JSON
            if "```json" in response:
                json_text = response.split("```json")[1].split("```")[0].strip()
            else:
                json_text = response

            data = json.loads(json_text)

            scores = {
                "novelty": float(data.get("novelty", 0.5)),
                "rigor": float(data.get("rigor", 0.5)),
                "clarity": float(data.get("clarity", 0.5)),
                "reproducibility": float(data.get("reproducibility", 0.5)),
                "impact": float(data.get("impact", 0.5)),
                "coherence": float(data.get("coherence", 0.5)),
                "limitations": float(data.get("limitations", 0.5)),
                "ethics": float(data.get("ethics", 0.5))
            }

            # Store reasoning if available
            scores["reasoning"] = data.get("reasoning", {})

            return scores

        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            # Return conservative defaults
            return {
                "novelty": 0.5,
                "rigor": 0.5,
                "clarity": 0.5,
                "reproducibility": 0.5,
                "impact": 0.5,
                "coherence": 0.5,
                "limitations": 0.5,
                "ethics": 0.5
            }

    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """
        Calculate weighted overall score.

        Rigor and Impact are weighted more heavily as they're most critical
        for scientific quality.
        """
        weights = {
            "novelty": 0.15,
            "rigor": 0.25,  # Most important
            "clarity": 0.10,
            "reproducibility": 0.15,
            "impact": 0.20,  # Second most important
            "coherence": 0.05,
            "limitations": 0.05,
            "ethics": 0.05
        }

        overall = sum(scores.get(dim, 0.5) * weight for dim, weight in weights.items())

        return round(overall, 3)

    def _generate_feedback(
        self,
        scores: Dict[str, float],
        passes: bool,
        finding: Dict[str, Any]
    ) -> str:
        """Generate human-readable feedback."""
        if passes:
            feedback = "✓ Finding passes quality threshold. "
        else:
            feedback = "✗ Finding does not meet quality threshold. "

        # Identify weak dimensions
        weak_dims = [dim for dim, score in scores.items()
                     if isinstance(score, float) and score < 0.6]

        if weak_dims:
            feedback += f"Weak dimensions: {', '.join(weak_dims)}. "

        # Specific feedback
        if scores.get("rigor", 1.0) < self.min_rigor_score:
            feedback += "Insufficient statistical rigor. "

        if self.require_citations and not finding.get('citations'):
            feedback += "Missing literature support. "

        if scores.get("clarity", 1.0) < 0.6:
            feedback += "Finding needs clearer presentation. "

        # Highlight strengths
        strong_dims = [dim for dim, score in scores.items()
                       if isinstance(score, float) and score >= 0.8]
        if strong_dims:
            feedback += f"Strengths: {', '.join(strong_dims)}."

        return feedback.strip()

    async def batch_evaluate(
        self,
        findings: List[Dict[str, Any]]
    ) -> List[ScholarEvalScore]:
        """
        Evaluate multiple findings in parallel.

        Args:
            findings: List of findings to evaluate

        Returns:
            List of ScholarEvalScore results
        """
        tasks = [self.evaluate_finding(f) for f in findings]
        return await asyncio.gather(*tasks)

    def get_validation_report(
        self,
        scores: List[ScholarEvalScore]
    ) -> str:
        """
        Generate validation report for multiple findings.

        Args:
            scores: List of evaluation scores

        Returns:
            Markdown report
        """
        report = "# ScholarEval Validation Report\n\n"
        report += f"**Total Findings Evaluated**: {len(scores)}\n"

        passed = sum(1 for s in scores if s.passes_threshold)
        report += f"**Passed Threshold**: {passed}/{len(scores)} ({passed/len(scores):.0%})\n\n"

        # Average scores
        if scores:
            avg_scores = {
                "Novelty": sum(s.novelty for s in scores) / len(scores),
                "Rigor": sum(s.rigor for s in scores) / len(scores),
                "Clarity": sum(s.clarity for s in scores) / len(scores),
                "Reproducibility": sum(s.reproducibility for s in scores) / len(scores),
                "Impact": sum(s.impact for s in scores) / len(scores),
                "Coherence": sum(s.coherence for s in scores) / len(scores),
                "Limitations": sum(s.limitations for s in scores) / len(scores),
                "Ethics": sum(s.ethics for s in scores) / len(scores)
            }

            report += "## Average Dimension Scores\n\n"
            for dim, score in avg_scores.items():
                report += f"- **{dim}**: {score:.2f}\n"

            report += f"\n**Overall Average**: {sum(s.overall_score for s in scores) / len(scores):.2f}\n"

        return report
