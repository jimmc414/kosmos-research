"""
Hybrid State Manager Demo for Kosmos

Demonstrates the hybrid architecture combining:
1. File artifacts (karpathy pattern) - Human-readable persistence
2. Neo4j knowledge graph (scientific-skills) - Relationship queries
3. Vector search (claude-skills-mcp) - Semantic similarity
4. Citation graph (scientific-writer) - Provenance tracking

This solves Gap 1 (State Manager Architecture) by showing:
- Schema design (entities and relationships)
- Storage architecture (hybrid approach)
- Update mechanisms (agents → artifacts → indexing)
- Query interface (find, read, list)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import sqlite3  # Using SQLite as mock for Neo4j
from datetime import datetime


class HybridStateManager:
    """
    Hybrid State Manager for Kosmos

    Architecture:
    - Layer 1: File artifacts (sandbox/) - karpathy pattern
    - Layer 2: Graph database (Neo4j mock) - scientific-skills pattern
    - Layer 3: Vector embeddings (mock) - claude-skills-mcp pattern
    - Layer 4: Citation graph - scientific-writer pattern
    """

    def __init__(self, sandbox_dir: str = "sandbox"):
        self.sandbox = Path(sandbox_dir)
        self.sandbox.mkdir(exist_ok=True)

        # Mock Neo4j with SQLite (for demo)
        # In production: use neo4j driver
        self.db_path = self.sandbox / "state_manager.db"
        self.conn = self._init_db()

        # Mock vector store (in production: use Pinecone/Weaviate)
        self.embeddings = {}

        # Citation graph
        self.citations = {}

    def _init_db(self) -> sqlite3.Connection:
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables for graph entities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id TEXT PRIMARY KEY,
                cycle INTEGER,
                task INTEGER,
                summary TEXT,
                p_value REAL,
                confidence REAL,
                notebook_path TEXT,
                timestamp TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hypotheses (
                id TEXT PRIMARY KEY,
                text TEXT,
                confidence REAL,
                validated BOOLEAN,
                created_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                target_id TEXT,
                relationship_type TEXT,
                confidence REAL,
                evidence TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                finding_id TEXT,
                pmid TEXT,
                title TEXT,
                authors TEXT
            )
        """)

        conn.commit()
        return conn

    async def add_finding(self, cycle: int, task: int, finding: Dict):
        """
        Add a finding using all 4 storage layers

        This demonstrates the full update pipeline:
        Agent output → File artifact → Graph indexing → Vector indexing → Citation tracking
        """
        finding_id = finding["id"]

        # Layer 1: Save file artifact (karpathy pattern)
        artifact_path = self._save_artifact(cycle, task, finding)

        # Layer 2: Index to graph database
        self._index_to_graph(finding)

        # Layer 3: Generate and store embedding
        self._index_to_vector_store(finding)

        # Layer 4: Track citations
        if finding.get("citations"):
            self._track_citations(finding_id, finding["citations"])

        print(f"✓ Added finding {finding_id} to all 4 storage layers")
        print(f"  - Artifact: {artifact_path}")
        print(f"  - Graph: Indexed with relationships")
        print(f"  - Vector: Embedded for semantic search")
        print(f"  - Citations: {len(finding.get('citations', []))} papers tracked")

    def _save_artifact(self, cycle: int, task: int, finding: Dict) -> Path:
        """
        Layer 1: Save as JSON artifact

        Pattern from: karpathy (artifact-based communication)
        Benefits: Human-readable, version-controllable, debuggable
        """
        cycle_dir = self.sandbox / f"cycle_{cycle}"
        cycle_dir.mkdir(exist_ok=True)

        artifact_path = cycle_dir / f"task_{task}_findings.json"

        artifact_data = {
            "finding_id": finding["id"],
            "cycle": cycle,
            "task": task,
            "summary": finding["summary"],
            "statistics": finding["statistics"],
            "notebook_path": str(finding["notebook_path"]),
            "timestamp": finding["timestamp"],
            "citations": finding.get("citations", [])
        }

        with open(artifact_path, "w") as f:
            json.dump(artifact_data, f, indent=2)

        return artifact_path

    def _index_to_graph(self, finding: Dict):
        """
        Layer 2: Index to graph database

        Pattern from: scientific-skills (Neo4j knowledge graph)
        Benefits: Relationship queries, provenance tracking
        """
        cursor = self.conn.cursor()

        # Insert finding node
        cursor.execute("""
            INSERT OR REPLACE INTO findings
            (id, cycle, task, summary, p_value, confidence, notebook_path, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            finding["id"],
            finding.get("cycle", 0),
            finding.get("task", 0),
            finding["summary"],
            finding["statistics"].get("p_value"),
            finding["statistics"].get("confidence"),
            str(finding["notebook_path"]),
            finding["timestamp"]
        ))

        # Create relationships
        if finding.get("supports_hypothesis"):
            cursor.execute("""
                INSERT INTO relationships
                (source_id, target_id, relationship_type, confidence, evidence)
                VALUES (?, ?, ?, ?, ?)
            """, (
                finding["id"],
                finding["supports_hypothesis"],
                "SUPPORTS",
                finding["statistics"].get("confidence", 0.5),
                finding["summary"]
            ))

        if finding.get("refutes_hypothesis"):
            cursor.execute("""
                INSERT INTO relationships
                (source_id, target_id, relationship_type, confidence, evidence)
                VALUES (?, ?, ?, ?, ?)
            """, (
                finding["id"],
                finding["refutes_hypothesis"],
                "REFUTES",
                finding["statistics"].get("confidence", 0.5),
                finding["summary"]
            ))

        self.conn.commit()

    def _index_to_vector_store(self, finding: Dict):
        """
        Layer 3: Generate vector embedding

        Pattern from: claude-skills-mcp (sentence-transformers)
        Benefits: Semantic search, novelty detection
        """
        # In production: Use sentence-transformers
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer('all-MiniLM-L6-v2')
        # embedding = model.encode(finding["summary"])

        # Mock embedding (random vector for demo)
        import random
        embedding = [random.random() for _ in range(384)]  # 384 dims like all-MiniLM-L6-v2

        self.embeddings[finding["id"]] = {
            "embedding": embedding,
            "finding": finding
        }

    def _track_citations(self, finding_id: str, citations: List[Dict]):
        """
        Layer 4: Track citations

        Pattern from: scientific-writer (citation graph)
        Benefits: Provenance, traceability, literature links
        """
        cursor = self.conn.cursor()

        for citation in citations:
            cursor.execute("""
                INSERT INTO citations
                (finding_id, pmid, title, authors)
                VALUES (?, ?, ?, ?)
            """, (
                finding_id,
                citation.get("pmid", ""),
                citation.get("title", ""),
                citation.get("authors", "")
            ))

        self.conn.commit()

    def query_similar_findings(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Semantic search for similar findings

        Uses Layer 3 (vector store)
        """
        # In production: compute query embedding and cosine similarity
        # For demo: return first k findings
        findings = list(self.embeddings.values())[:top_k]
        return [f["finding"] for f in findings]

    def query_graph(self, query_type: str, params: Dict = None) -> List[Dict]:
        """
        Query knowledge graph

        Uses Layer 2 (Neo4j mock)
        """
        cursor = self.conn.cursor()

        if query_type == "high_confidence":
            cursor.execute("""
                SELECT * FROM findings
                WHERE confidence > ?
                ORDER BY confidence DESC
            """, (params.get("min_confidence", 0.9),))

        elif query_type == "supports_hypothesis":
            cursor.execute("""
                SELECT f.* FROM findings f
                JOIN relationships r ON f.id = r.source_id
                WHERE r.target_id = ? AND r.relationship_type = 'SUPPORTS'
            """, (params.get("hypothesis_id"),))

        elif query_type == "recent_findings":
            cursor.execute("""
                SELECT * FROM findings
                WHERE cycle >= ?
                ORDER BY cycle DESC, task DESC
                LIMIT ?
            """, (params.get("min_cycle", 1), params.get("limit", 10)))

        else:
            cursor.execute("SELECT * FROM findings LIMIT 10")

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def get_finding_provenance(self, finding_id: str) -> Dict:
        """
        Get complete provenance chain for a finding

        Uses all 4 layers:
        - Graph: Relationship queries
        - Artifacts: File paths
        - Citations: Paper links
        - Vector: Similar findings
        """
        # Query graph for relationships
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT target_id, relationship_type, confidence
            FROM relationships
            WHERE source_id = ?
        """, (finding_id,))

        relationships = [
            {
                "target": row[0],
                "type": row[1],
                "confidence": row[2]
            }
            for row in cursor.fetchall()
        ]

        # Get finding details
        cursor.execute("""
            SELECT cycle, task, notebook_path
            FROM findings
            WHERE id = ?
        """, (finding_id,))

        row = cursor.fetchone()
        if not row:
            return {"error": "Finding not found"}

        cycle, task, notebook_path = row

        # Get artifact
        artifact_path = self.sandbox / f"cycle_{cycle}" / f"task_{task}_findings.json"
        if artifact_path.exists():
            with open(artifact_path) as f:
                artifact = json.load(f)
        else:
            artifact = None

        # Get citations
        cursor.execute("""
            SELECT pmid, title, authors
            FROM citations
            WHERE finding_id = ?
        """, (finding_id,))

        citations = [
            {
                "pmid": row[0],
                "title": row[1],
                "authors": row[2]
            }
            for row in cursor.fetchall()
        ]

        return {
            "finding_id": finding_id,
            "relationships": relationships,
            "artifact_path": str(artifact_path),
            "artifact": artifact,
            "citations": citations,
            "notebook_path": notebook_path
        }

    def generate_cycle_summary(self, cycle: int) -> str:
        """
        Generate summary for a cycle

        Queries all findings from this cycle and creates markdown summary
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT id, task, summary, p_value, confidence
            FROM findings
            WHERE cycle = ?
            ORDER BY task
        """, (cycle,))

        findings = cursor.fetchall()

        summary = f"# Cycle {cycle} Summary\n\n"
        summary += f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        summary += f"**Findings**: {len(findings)}\n\n"

        summary += "## Key Findings\n\n"
        for finding_id, task, finding_summary, p_value, confidence in findings:
            summary += f"### Task {task}: {finding_id}\n\n"
            summary += f"{finding_summary}\n\n"
            if p_value:
                summary += f"- **p-value**: {p_value:.2e}\n"
            if confidence:
                summary += f"- **Confidence**: {confidence:.2%}\n"
            summary += "\n"

        # Save summary artifact
        cycle_dir = self.sandbox / f"cycle_{cycle}"
        summary_path = cycle_dir / f"cycle_{cycle}_summary.md"
        with open(summary_path, "w") as f:
            f.write(summary)

        return summary

    def query_interface_demo(self):
        """
        Demonstrate the 3-tier query interface (claude-skills-mcp pattern)

        Tools:
        1. find_findings - Semantic search for relevant findings
        2. read_evidence - Retrieve specific artifacts and notebooks
        3. list_all - View complete inventory
        """
        print("\n" + "=" * 80)
        print("QUERY INTERFACE DEMO (MCP Pattern)")
        print("=" * 80)

        print("\n1. find_findings(query='cancer gene expression')")
        similar = self.query_similar_findings("cancer gene expression", top_k=3)
        for f in similar:
            print(f"   - {f['summary']}")

        print("\n2. read_evidence(finding_id='finding_1_1')")
        provenance = self.get_finding_provenance("finding_1_1")
        print(f"   - Notebook: {provenance.get('notebook_path', 'N/A')}")
        print(f"   - Citations: {len(provenance.get('citations', []))} papers")
        print(f"   - Relationships: {len(provenance.get('relationships', []))} connections")

        print("\n3. list_all(min_confidence=0.9)")
        high_conf = self.query_graph("high_confidence", {"min_confidence": 0.9})
        print(f"   - Found {len(high_conf)} high-confidence findings")
        for finding in high_conf[:3]:
            print(f"     • {finding['summary']} (conf={finding['confidence']:.2f})")


async def demo():
    """Demonstrate hybrid state manager"""
    print("=" * 80)
    print("HYBRID STATE MANAGER DEMO")
    print("=" * 80)
    print()
    print("Architecture:")
    print("  Layer 1: File artifacts (karpathy)")
    print("  Layer 2: Graph database (scientific-skills)")
    print("  Layer 3: Vector search (claude-skills-mcp)")
    print("  Layer 4: Citation graph (scientific-writer)")
    print()

    state_manager = HybridStateManager(sandbox_dir="sandbox_demo")

    # Add some findings
    findings = [
        {
            "id": "finding_1_1",
            "cycle": 1,
            "task": 1,
            "summary": "BRCA1 gene shows significant upregulation in cancer cells (p=0.001, FC=2.5)",
            "statistics": {
                "p_value": 0.001,
                "fold_change": 2.5,
                "confidence": 0.95
            },
            "notebook_path": Path("cycle_1/task_1_brca1_analysis.ipynb"),
            "timestamp": "2025-11-22T10:00:00",
            "supports_hypothesis": "hyp_1",
            "citations": [
                {"pmid": "12345678", "title": "BRCA1 in breast cancer", "authors": "Smith et al."},
                {"pmid": "23456789", "title": "BRCA1 regulatory mechanisms", "authors": "Jones et al."}
            ]
        },
        {
            "id": "finding_1_2",
            "cycle": 1,
            "task": 2,
            "summary": "TP53 mutation frequency is 45% in tumor samples (p=0.005)",
            "statistics": {
                "p_value": 0.005,
                "frequency": 0.45,
                "confidence": 0.90
            },
            "notebook_path": Path("cycle_1/task_2_tp53_analysis.ipynb"),
            "timestamp": "2025-11-22T10:30:00",
            "citations": [
                {"pmid": "34567890", "title": "TP53 mutations in cancer", "authors": "Brown et al."}
            ]
        },
        {
            "id": "finding_2_1",
            "cycle": 2,
            "task": 1,
            "summary": "BRCA1-TP53 interaction network identified (correlation r=0.85, p<0.001)",
            "statistics": {
                "p_value": 0.0001,
                "correlation": 0.85,
                "confidence": 0.96
            },
            "notebook_path": Path("cycle_2/task_1_network_analysis.ipynb"),
            "timestamp": "2025-11-22T11:00:00",
            "supports_hypothesis": "hyp_1",
            "citations": []
        }
    ]

    print("=" * 80)
    print("ADDING FINDINGS TO STATE MANAGER")
    print("=" * 80)
    print()

    for finding in findings:
        await state_manager.add_finding(
            cycle=finding["cycle"],
            task=finding["task"],
            finding=finding
        )
        print()

    # Query examples
    print("\n" + "=" * 80)
    print("GRAPH QUERIES")
    print("=" * 80)

    print("\n1. High confidence findings (>0.9):")
    high_conf = state_manager.query_graph("high_confidence", {"min_confidence": 0.9})
    for f in high_conf:
        print(f"   - {f['summary']} (conf={f['confidence']:.2f})")

    print("\n2. Findings supporting hypothesis 'hyp_1':")
    supporting = state_manager.query_graph("supports_hypothesis", {"hypothesis_id": "hyp_1"})
    for f in supporting:
        print(f"   - {f['summary']}")

    print("\n3. Recent findings (cycle >= 2):")
    recent = state_manager.query_graph("recent_findings", {"min_cycle": 2, "limit": 5})
    for f in recent:
        print(f"   - Cycle {f['cycle']}, Task {f['task']}: {f['summary']}")

    # Provenance example
    print("\n" + "=" * 80)
    print("PROVENANCE TRACKING")
    print("=" * 80)
    print("\nComplete provenance for finding_1_1:")

    provenance = state_manager.get_finding_provenance("finding_1_1")
    print(f"  - Finding ID: {provenance['finding_id']}")
    print(f"  - Notebook: {provenance['notebook_path']}")
    print(f"  - Artifact: {provenance['artifact_path']}")
    print(f"  - Relationships:")
    for rel in provenance['relationships']:
        print(f"    • {rel['type']} {rel['target']} (confidence={rel['confidence']:.2f})")
    print(f"  - Citations: {len(provenance['citations'])} papers")
    for cit in provenance['citations']:
        print(f"    • {cit['pmid']}: {cit['title']}")

    # Cycle summary
    print("\n" + "=" * 80)
    print("CYCLE SUMMARY GENERATION")
    print("=" * 80)

    summary = state_manager.generate_cycle_summary(cycle=1)
    print(summary)

    # Query interface demo
    state_manager.query_interface_demo()

    print("\n" + "=" * 80)
    print("ARCHITECTURE BENEFITS")
    print("=" * 80)
    print()
    print("Layer 1 (File Artifacts):")
    print("  ✓ Human-readable JSON files")
    print("  ✓ Version control friendly")
    print("  ✓ Easy debugging")
    print()
    print("Layer 2 (Graph Database):")
    print("  ✓ Relationship queries (SUPPORTS, REFUTES)")
    print("  ✓ Provenance tracking")
    print("  ✓ Complex graph traversals")
    print()
    print("Layer 3 (Vector Search):")
    print("  ✓ Semantic similarity")
    print("  ✓ Novelty detection")
    print("  ✓ Find similar findings")
    print()
    print("Layer 4 (Citation Graph):")
    print("  ✓ Literature traceability")
    print("  ✓ Claim → evidence links")
    print("  ✓ Complete provenance chain")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demo())
