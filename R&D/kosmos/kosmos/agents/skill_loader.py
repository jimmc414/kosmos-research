"""
Scientific Skills Loader for Kosmos Agents.

This module integrates the claude-scientific-skills collection into Kosmos agents,
providing domain-specific expertise and code examples for data analysis tasks.

Pattern source: R&D/kosmos-claude-scientific-skills
Gap addressed: Gap 3 (Agent Integration & System Prompts)

The scientific-skills collection provides:
- 120+ specialized skills for scientific domains
- Working code examples for each library
- Best practices and domain expertise
- API documentation and references

Usage:
    loader = SkillLoader()

    # Load skills for a specific task
    skills = loader.load_skills_for_task(
        task_type="single_cell_analysis",
        libraries=["scanpy", "anndata"]
    )

    # Inject into agent prompt
    prompt = f'''
    You are a data analysis expert with the following skills:

    {skills}

    Now analyze...
    '''
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Set
import yaml

logger = logging.getLogger(__name__)


class SkillLoader:
    """
    Loader for scientific skills to enhance agent capabilities.

    This integrates the claude-scientific-skills collection by loading
    relevant SKILL.md files based on task requirements.
    """

    def __init__(self, skills_dir: Optional[str] = None):
        """
        Initialize skill loader.

        Args:
            skills_dir: Path to scientific-skills directory
                        If None, looks for it in R&D/kosmos-claude-scientific-skills
        """
        if skills_dir is None:
            # Try to find skills in R&D directory
            project_root = Path(__file__).parent.parent.parent.parent
            skills_dir = project_root / "kosmos-claude-scientific-skills" / "scientific-skills"

        self.skills_dir = Path(skills_dir)

        # Mapping of task types to relevant skills
        self.task_skill_mapping = {
            "single_cell_analysis": ["scanpy", "anndata", "scvi-tools"],
            "genomics": ["biopython", "pysam", "gget"],
            "cheminformatics": ["rdkit", "datamol", "deepchem"],
            "drug_discovery": ["rdkit", "datamol", "deepchem", "diffdock"],
            "proteomics": ["pyopenms", "matchms"],
            "machine_learning": ["pytorch-lightning", "transformers", "scikit-learn"],
            "time_series": ["aeon"],
            "network_analysis": ["networkx", "torch-geometric"],
            "statistical_analysis": ["statsmodels", "scikit-learn"],
            "pathway_analysis": ["gseapy"],
            "literature_review": ["pubmed-database", "openalex-database"],
            "data_processing": ["dask", "polars", "vaex"],
            "visualization": ["matplotlib", "seaborn"],
        }

    def load_skill(self, skill_name: str) -> Optional[Dict[str, str]]:
        """
        Load a single skill from SKILL.md file.

        Args:
            skill_name: Name of the skill (e.g., "scanpy")

        Returns:
            Dict with skill content:
            {
                "name": "scanpy",
                "description": "...",
                "usage": "...",
                "examples": "...",
                "full_content": "..."
            }
            or None if skill not found
        """
        skill_path = self.skills_dir / skill_name / "SKILL.md"

        if not skill_path.exists():
            logger.warning(f"Skill not found: {skill_name} at {skill_path}")
            return None

        with open(skill_path) as f:
            content = f.read()

        # Parse YAML frontmatter if present
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                except yaml.YAMLError:
                    frontmatter = {}
                    body = content
            else:
                frontmatter = {}
                body = content
        else:
            frontmatter = {}
            body = content

        # Extract sections
        description = self._extract_section(body, "description") or frontmatter.get("description", "")
        usage = self._extract_section(body, "usage") or self._extract_section(body, "quick start")
        examples = self._extract_section(body, "examples")

        return {
            "name": skill_name,
            "description": description,
            "usage": usage,
            "examples": examples,
            "full_content": body,
            "metadata": frontmatter
        }

    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract a section from markdown content."""
        lines = content.split("\n")
        section_lines = []
        in_section = False
        section_header = f"## {section_name}"

        for line in lines:
            if line.lower().startswith(section_header.lower()):
                in_section = True
                continue
            elif in_section and line.startswith("##"):
                break
            elif in_section:
                section_lines.append(line)

        return "\n".join(section_lines).strip() if section_lines else None

    def load_skills_for_task(
        self,
        task_type: Optional[str] = None,
        libraries: Optional[List[str]] = None,
        include_examples: bool = True
    ) -> str:
        """
        Load relevant skills for a task.

        Args:
            task_type: Type of task (e.g., "single_cell_analysis")
            libraries: Specific libraries needed
            include_examples: Whether to include code examples

        Returns:
            Formatted string with skill documentation
        """
        # Determine which skills to load
        skills_to_load: Set[str] = set()

        if task_type and task_type in self.task_skill_mapping:
            skills_to_load.update(self.task_skill_mapping[task_type])

        if libraries:
            skills_to_load.update(libraries)

        if not skills_to_load:
            logger.warning("No skills specified, loading general analysis skills")
            skills_to_load = {"scikit-learn", "matplotlib", "statsmodels"}

        # Load skills
        loaded_skills = []
        for skill_name in skills_to_load:
            skill = self.load_skill(skill_name)
            if skill:
                loaded_skills.append(skill)

        # Format for prompt injection
        return self._format_skills_for_prompt(loaded_skills, include_examples)

    def _format_skills_for_prompt(
        self,
        skills: List[Dict[str, str]],
        include_examples: bool
    ) -> str:
        """
        Format skills for injection into agent prompt.

        This creates a concise reference that gives the agent domain expertise
        without overwhelming the context window.
        """
        if not skills:
            return ""

        output = "# Available Scientific Skills\n\n"
        output += "You have access to the following specialized scientific skills:\n\n"

        for skill in skills:
            output += f"## {skill['name']}\n\n"

            if skill['description']:
                output += f"{skill['description']}\n\n"

            if skill['usage']:
                output += f"### Usage\n\n{skill['usage']}\n\n"

            if include_examples and skill['examples']:
                # Limit examples to keep context manageable
                examples = skill['examples']
                if len(examples) > 500:
                    examples = examples[:500] + "\n... (truncated for brevity)"

                output += f"### Examples\n\n{examples}\n\n"

            output += "---\n\n"

        return output

    def get_available_skills(self) -> List[str]:
        """
        Get list of all available skills.

        Returns:
            List of skill names
        """
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return []

        skills = []
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                skills.append(skill_dir.name)

        return sorted(skills)

    def get_task_types(self) -> List[str]:
        """Get list of supported task types."""
        return sorted(self.task_skill_mapping.keys())


# Predefined skill bundles for common tasks
SKILL_BUNDLES = {
    "cancer_research": [
        "scanpy",  # Single-cell analysis
        "pydeseq2",  # Differential expression
        "anndata",  # Data structures
        "gseapy",  # Pathway analysis
        "string-database",  # Protein interactions
        "cosmic-database",  # Cancer mutations
        "clinvar-database",  # Variant interpretation
    ],
    "drug_discovery": [
        "rdkit",  # Molecular manipulation
        "datamol",  # Molecular workflows
        "deepchem",  # ML for chemistry
        "chembl-database",  # Bioactivity data
        "pubchem-database",  # Chemical structures
        "zinc-database",  # Virtual screening
    ],
    "genomics_analysis": [
        "biopython",  # Sequence analysis
        "pysam",  # BAM/VCF handling
        "ensembl-database",  # Genome annotations
        "ncbi-gene-database",  # Gene info
        "gwas-catalog",  # GWAS variants
    ],
    "systems_biology": [
        "networkx",  # Network analysis
        "torch-geometric",  # Graph ML
        "string-database",  # PPI networks
        "kegg-database",  # Pathways
        "reactome-database",  # Pathway enrichment
        "cobrapy",  # Metabolic modeling
    ],
    "clinical_research": [
        "clinvar-database",  # Variant pathogenicity
        "clinicaltrials-database",  # Trial data
        "clinpgx-database",  # Pharmacogenomics
        "cosmic-database",  # Somatic mutations
        "opentargets-database",  # Drug targets
    ]
}


def load_skill_bundle(bundle_name: str, loader: Optional[SkillLoader] = None) -> str:
    """
    Load a predefined bundle of skills.

    Args:
        bundle_name: Name of the bundle (see SKILL_BUNDLES)
        loader: Optional SkillLoader instance

    Returns:
        Formatted skills string
    """
    if bundle_name not in SKILL_BUNDLES:
        raise ValueError(f"Unknown skill bundle: {bundle_name}. Available: {list(SKILL_BUNDLES.keys())}")

    if loader is None:
        loader = SkillLoader()

    skills = SKILL_BUNDLES[bundle_name]
    return loader.load_skills_for_task(libraries=skills)
