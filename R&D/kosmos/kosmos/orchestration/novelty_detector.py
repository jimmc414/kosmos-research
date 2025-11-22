"""
Novelty Detection for Task Planning.

This module uses vector embeddings to detect redundant tasks and ensure
research plans explore new directions rather than repeating past work.

Pattern source: R&D/kosmos-karpathy (novelty scoring)
Gap addressed: Gap 2 (Task Generation Strategy)

The novelty detector:
1. Embeds tasks, findings, and hypotheses using sentence-transformers
2. Computes semantic similarity between proposed and past work
3. Flags tasks below novelty threshold for revision
4. Maintains vector index for fast similarity search
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning(
        "sentence-transformers not installed. "
        "Novelty detection will use fallback keyword matching. "
        "Install with: pip install sentence-transformers"
    )
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class NoveltyDetector:
    """
    Detects redundant tasks using semantic similarity.

    This helps ensure research plans explore new directions
    rather than repeating past work.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        novelty_threshold: float = 0.75,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize novelty detector.

        Args:
            model_name: Sentence transformer model to use
                       'all-MiniLM-L6-v2' is fast and effective (default)
                       'all-mpnet-base-v2' is more accurate but slower
            novelty_threshold: Similarity threshold (0-1)
                             Tasks with similarity > threshold are flagged as redundant
                             Default 0.75 means tasks must be <75% similar to past work
            cache_dir: Directory to cache embeddings
        """
        self.novelty_threshold = novelty_threshold
        self.cache_dir = Path(cache_dir) if cache_dir else None

        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                self.use_embeddings = True
                logger.info(f"Loaded sentence transformer: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer: {e}. Using fallback.")
                self.use_embeddings = False
        else:
            self.use_embeddings = False

        # Vector index
        self.task_embeddings: List[np.ndarray] = []
        self.task_texts: List[str] = []
        self.task_metadata: List[Dict] = []

        # Finding embeddings
        self.finding_embeddings: List[np.ndarray] = []
        self.finding_texts: List[str] = []
        self.finding_metadata: List[Dict] = []

    def index_past_tasks(self, tasks: List[Dict[str, Any]]):
        """
        Index past tasks for similarity comparison.

        Args:
            tasks: List of past task dicts with 'description' field
        """
        if not tasks:
            return

        logger.info(f"Indexing {len(tasks)} past tasks")

        # Extract task descriptions
        task_texts = []
        for task in tasks:
            description = task.get("description", "")
            task_type = task.get("type", "unknown")
            # Combine type and description for better matching
            text = f"{task_type}: {description}"
            task_texts.append(text)

        # Generate embeddings
        if self.use_embeddings:
            try:
                embeddings = self.model.encode(task_texts, convert_to_numpy=True)
                self.task_embeddings.extend(embeddings)
                self.task_texts.extend(task_texts)
                self.task_metadata.extend(tasks)
                logger.info(f"Indexed {len(embeddings)} task embeddings")
            except Exception as e:
                logger.error(f"Failed to generate embeddings: {e}")
                # Fall back to text matching
                self.task_texts.extend(task_texts)
                self.task_metadata.extend(tasks)
        else:
            # Just store texts for keyword matching
            self.task_texts.extend(task_texts)
            self.task_metadata.extend(tasks)

    def index_findings(self, findings: List[Dict[str, Any]]):
        """
        Index past findings for similarity comparison.

        Args:
            findings: List of finding dicts with 'summary' field
        """
        if not findings:
            return

        logger.info(f"Indexing {len(findings)} findings")

        # Extract finding summaries
        finding_texts = [f.get("summary", "") for f in findings]

        # Generate embeddings
        if self.use_embeddings:
            try:
                embeddings = self.model.encode(finding_texts, convert_to_numpy=True)
                self.finding_embeddings.extend(embeddings)
                self.finding_texts.extend(finding_texts)
                self.finding_metadata.extend(findings)
                logger.info(f"Indexed {len(embeddings)} finding embeddings")
            except Exception as e:
                logger.error(f"Failed to generate embeddings: {e}")
                self.finding_texts.extend(finding_texts)
                self.finding_metadata.extend(findings)
        else:
            self.finding_texts.extend(finding_texts)
            self.finding_metadata.extend(findings)

    def check_task_novelty(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if a task is novel compared to past work.

        Args:
            task: Task dict with 'description' field

        Returns:
            Dict with:
                - is_novel: bool (True if similarity < threshold)
                - max_similarity: float (0-1, highest similarity to past work)
                - similar_tasks: List of similar past tasks
                - similar_findings: List of similar findings
                - novelty_score: float (0-1, higher = more novel)
        """
        description = task.get("description", "")
        task_type = task.get("type", "unknown")
        text = f"{task_type}: {description}"

        if self.use_embeddings and self.task_embeddings:
            return self._check_novelty_embeddings(text, task)
        else:
            return self._check_novelty_keywords(text, task)

    def _check_novelty_embeddings(
        self,
        text: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check novelty using semantic embeddings."""
        try:
            # Encode proposed task
            task_embedding = self.model.encode([text], convert_to_numpy=True)[0]

            # Compute similarities to past tasks
            task_similarities = []
            if self.task_embeddings:
                task_embeddings_matrix = np.array(self.task_embeddings)
                similarities = np.dot(task_embeddings_matrix, task_embedding)
                task_similarities = similarities.tolist()

            # Compute similarities to findings
            finding_similarities = []
            if self.finding_embeddings:
                finding_embeddings_matrix = np.array(self.finding_embeddings)
                similarities = np.dot(finding_embeddings_matrix, task_embedding)
                finding_similarities = similarities.tolist()

            # Find maximum similarity
            max_task_sim = max(task_similarities) if task_similarities else 0.0
            max_finding_sim = max(finding_similarities) if finding_similarities else 0.0
            max_similarity = max(max_task_sim, max_finding_sim)

            # Calculate novelty score (inverse of similarity)
            novelty_score = 1.0 - max_similarity

            # Identify similar tasks (above 0.6 similarity)
            similar_tasks = []
            if task_similarities:
                for i, sim in enumerate(task_similarities):
                    if sim > 0.6:
                        similar_tasks.append({
                            "task": self.task_metadata[i],
                            "similarity": round(float(sim), 3)
                        })

            # Identify similar findings
            similar_findings = []
            if finding_similarities:
                for i, sim in enumerate(finding_similarities):
                    if sim > 0.6:
                        similar_findings.append({
                            "finding": self.finding_metadata[i],
                            "similarity": round(float(sim), 3)
                        })

            # Sort by similarity
            similar_tasks.sort(key=lambda x: x["similarity"], reverse=True)
            similar_findings.sort(key=lambda x: x["similarity"], reverse=True)

            # Limit to top 3
            similar_tasks = similar_tasks[:3]
            similar_findings = similar_findings[:3]

            is_novel = max_similarity < self.novelty_threshold

            logger.debug(
                f"Task novelty check: max_sim={max_similarity:.3f}, "
                f"novel={is_novel}, threshold={self.novelty_threshold}"
            )

            return {
                "is_novel": is_novel,
                "max_similarity": round(float(max_similarity), 3),
                "novelty_score": round(novelty_score, 3),
                "similar_tasks": similar_tasks,
                "similar_findings": similar_findings,
                "method": "embeddings"
            }

        except Exception as e:
            logger.error(f"Embedding-based novelty check failed: {e}")
            # Fall back to keyword matching
            return self._check_novelty_keywords(text, task)

    def _check_novelty_keywords(
        self,
        text: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback novelty check using keyword matching.

        This is less accurate than embeddings but works without dependencies.
        """
        text_lower = text.lower()
        text_words = set(text_lower.split())

        # Check against past tasks
        max_similarity = 0.0
        similar_tasks = []

        for i, past_text in enumerate(self.task_texts):
            past_words = set(past_text.lower().split())

            # Jaccard similarity
            intersection = text_words & past_words
            union = text_words | past_words

            if len(union) > 0:
                similarity = len(intersection) / len(union)

                if similarity > max_similarity:
                    max_similarity = similarity

                if similarity > 0.4:  # Lower threshold for keyword matching
                    similar_tasks.append({
                        "task": self.task_metadata[i] if i < len(self.task_metadata) else {},
                        "similarity": round(similarity, 3)
                    })

        # Check against findings
        similar_findings = []
        for i, finding_text in enumerate(self.finding_texts):
            finding_words = set(finding_text.lower().split())

            intersection = text_words & finding_words
            union = text_words | finding_words

            if len(union) > 0:
                similarity = len(intersection) / len(union)

                if similarity > max_similarity:
                    max_similarity = similarity

                if similarity > 0.4:
                    similar_findings.append({
                        "finding": self.finding_metadata[i] if i < len(self.finding_metadata) else {},
                        "similarity": round(similarity, 3)
                    })

        # Sort and limit
        similar_tasks.sort(key=lambda x: x["similarity"], reverse=True)
        similar_findings.sort(key=lambda x: x["similarity"], reverse=True)
        similar_tasks = similar_tasks[:3]
        similar_findings = similar_findings[:3]

        novelty_score = 1.0 - max_similarity
        is_novel = max_similarity < (self.novelty_threshold - 0.2)  # Lower threshold for keywords

        logger.debug(
            f"Task novelty check (keywords): max_sim={max_similarity:.3f}, "
            f"novel={is_novel}"
        )

        return {
            "is_novel": is_novel,
            "max_similarity": round(max_similarity, 3),
            "novelty_score": round(novelty_score, 3),
            "similar_tasks": similar_tasks,
            "similar_findings": similar_findings,
            "method": "keywords"
        }

    def check_plan_novelty(
        self,
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check novelty of entire plan.

        Args:
            plan: Plan with 'tasks' list

        Returns:
            Dict with:
                - average_novelty_score: float (0-1)
                - novel_task_count: int
                - redundant_task_count: int
                - task_novelty_details: List of per-task novelty checks
        """
        tasks = plan.get("tasks", [])

        if not tasks:
            return {
                "average_novelty_score": 1.0,
                "novel_task_count": 0,
                "redundant_task_count": 0,
                "task_novelty_details": []
            }

        # Check each task
        task_novelty_details = []
        novelty_scores = []

        for task in tasks:
            novelty_check = self.check_task_novelty(task)
            task_novelty_details.append({
                "task_id": task.get("id"),
                "task_description": task.get("description"),
                **novelty_check
            })
            novelty_scores.append(novelty_check["novelty_score"])

        # Calculate statistics
        average_novelty = sum(novelty_scores) / len(novelty_scores)
        novel_count = sum(1 for check in task_novelty_details if check["is_novel"])
        redundant_count = len(tasks) - novel_count

        logger.info(
            f"Plan novelty: avg={average_novelty:.3f}, "
            f"novel={novel_count}/{len(tasks)}, redundant={redundant_count}"
        )

        return {
            "average_novelty_score": round(average_novelty, 3),
            "novel_task_count": novel_count,
            "redundant_task_count": redundant_count,
            "task_novelty_details": task_novelty_details
        }

    def save_index(self, filepath: str):
        """
        Save vector index to disk.

        Args:
            filepath: Path to save index
        """
        index_data = {
            "task_texts": self.task_texts,
            "task_metadata": self.task_metadata,
            "finding_texts": self.finding_texts,
            "finding_metadata": self.finding_metadata,
            "use_embeddings": self.use_embeddings,
            "novelty_threshold": self.novelty_threshold
        }

        # Save embeddings separately as numpy arrays
        if self.use_embeddings:
            index_path = Path(filepath)
            index_path.parent.mkdir(parents=True, exist_ok=True)

            # Save metadata as JSON
            with open(filepath, "w") as f:
                json.dump(index_data, f, indent=2)

            # Save embeddings as numpy arrays
            if self.task_embeddings:
                np.save(
                    str(index_path.parent / f"{index_path.stem}_task_embeddings.npy"),
                    np.array(self.task_embeddings)
                )

            if self.finding_embeddings:
                np.save(
                    str(index_path.parent / f"{index_path.stem}_finding_embeddings.npy"),
                    np.array(self.finding_embeddings)
                )

            logger.info(f"Saved novelty index to {filepath}")
        else:
            # Just save texts and metadata
            with open(filepath, "w") as f:
                json.dump(index_data, f, indent=2)

            logger.info(f"Saved novelty index (no embeddings) to {filepath}")

    def load_index(self, filepath: str):
        """
        Load vector index from disk.

        Args:
            filepath: Path to load index from
        """
        index_path = Path(filepath)

        if not index_path.exists():
            logger.warning(f"Index file not found: {filepath}")
            return

        # Load metadata
        with open(filepath) as f:
            index_data = json.load(f)

        self.task_texts = index_data.get("task_texts", [])
        self.task_metadata = index_data.get("task_metadata", [])
        self.finding_texts = index_data.get("finding_texts", [])
        self.finding_metadata = index_data.get("finding_metadata", [])

        # Load embeddings if available
        if index_data.get("use_embeddings") and self.use_embeddings:
            task_emb_path = index_path.parent / f"{index_path.stem}_task_embeddings.npy"
            finding_emb_path = index_path.parent / f"{index_path.stem}_finding_embeddings.npy"

            if task_emb_path.exists():
                self.task_embeddings = list(np.load(str(task_emb_path)))
                logger.info(f"Loaded {len(self.task_embeddings)} task embeddings")

            if finding_emb_path.exists():
                self.finding_embeddings = list(np.load(str(finding_emb_path)))
                logger.info(f"Loaded {len(self.finding_embeddings)} finding embeddings")

        logger.info(f"Loaded novelty index from {filepath}")

    def reset(self):
        """Clear all indexed data."""
        self.task_embeddings.clear()
        self.task_texts.clear()
        self.task_metadata.clear()
        self.finding_embeddings.clear()
        self.finding_texts.clear()
        self.finding_metadata.clear()
        logger.info("Reset novelty detector")
