"""
Technique Extraction Service

Extracts structured technique/method information from papers using:
1. LLM-based extraction (Gemini) for rich semantics
2. Heuristic fallback for when LLM is unavailable
3. Normalization and deduplication

The extracted techniques feed into the knowledge graph and enable:
- Technique-based search and filtering
- Method comparison views
- Technique evolution timelines
- Trend detection
"""
from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Set

from pydantic import BaseModel
import google.generativeai as genai

from app.core.config import settings
from app.utils.logger import LoggerMixin


class ExtractedTechnique(BaseModel):
    """A technique/method extracted from a paper"""
    name: str
    normalized_name: str
    category: Optional[str] = None  # e.g., "attention", "normalization", "optimization"
    technique_type: Optional[str] = None  # e.g., "architecture", "training", "data"
    is_primary: bool = False  # Is this the main contribution?
    confidence: float = 0.8
    related_techniques: List[str] = []
    description: Optional[str] = None


class TechniqueExtractionResult(BaseModel):
    """Result of technique extraction for a paper"""
    paper_id: str
    techniques: List[ExtractedTechnique]
    architecture_type: Optional[str] = None  # e.g., "transformer", "cnn", "diffusion"
    task_domains: List[str] = []  # e.g., ["NLP", "vision"]
    novelty_type: Optional[str] = None  # e.g., "method", "dataset", "analysis"
    key_components: List[str] = []
    extraction_method: str = "unknown"  # "llm" or "heuristic"


# Common technique patterns for heuristic extraction
TECHNIQUE_PATTERNS = {
    # Architectures
    "transformer": ["transformer", "attention mechanism", "self-attention", "multi-head attention"],
    "diffusion": ["diffusion", "score matching", "denoising", "ddpm", "ddim"],
    "cnn": ["convolutional", "cnn", "convnet", "resnet", "vgg", "efficientnet"],
    "rnn": ["recurrent", "lstm", "gru", "sequence model"],
    "gan": ["generative adversarial", "gan", "discriminator", "generator"],
    "vae": ["variational autoencoder", "vae", "latent space", "elbo"],
    "moe": ["mixture of experts", "moe", "sparse gating"],
    "ssm": ["state space", "mamba", "s4", "structured state"],

    # Training techniques
    "lora": ["lora", "low-rank adaptation", "low rank"],
    "qlora": ["qlora", "quantized lora"],
    "peft": ["parameter-efficient", "peft", "adapter", "prefix tuning", "prompt tuning"],
    "distillation": ["distillation", "knowledge distillation", "teacher-student"],
    "contrastive": ["contrastive learning", "simclr", "clip", "infonce"],
    "rlhf": ["rlhf", "reinforcement learning from human feedback", "reward model"],
    "dpo": ["dpo", "direct preference optimization"],

    # Normalization/regularization
    "layer_norm": ["layer normalization", "layernorm", "ln"],
    "batch_norm": ["batch normalization", "batchnorm", "bn"],
    "dropout": ["dropout", "droppath", "stochastic depth"],
    "rmsnorm": ["rmsnorm", "rms normalization"],

    # Attention variants
    "flash_attention": ["flash attention", "flashattention"],
    "sparse_attention": ["sparse attention", "longformer", "bigbird"],
    "linear_attention": ["linear attention", "performer", "linformer"],
    "cross_attention": ["cross attention", "cross-attention"],

    # Optimization
    "adam": ["adam optimizer", "adamw"],
    "lion": ["lion optimizer"],
    "schedule_free": ["schedule-free", "schedule free"],
    "warmup": ["learning rate warmup", "lr warmup"],
    "cosine_decay": ["cosine decay", "cosine annealing", "cosine schedule"],
}

# Task domain keywords
TASK_DOMAINS = {
    "nlp": ["language", "text", "nlp", "translation", "summarization", "qa", "question answering"],
    "vision": ["image", "vision", "visual", "object detection", "segmentation", "classification"],
    "speech": ["speech", "audio", "asr", "tts", "voice"],
    "multimodal": ["multimodal", "vision-language", "image-text", "clip"],
    "reinforcement_learning": ["reinforcement learning", "rl", "policy", "reward", "agent"],
    "generation": ["generation", "generative", "synthesis", "creation"],
    "reasoning": ["reasoning", "chain of thought", "cot", "step-by-step"],
    "robotics": ["robotics", "robot", "manipulation", "navigation"],
    "graphs": ["graph neural", "gnn", "node", "edge", "knowledge graph"],
}


class TechniqueExtractionService(LoggerMixin):
    """
    Service for extracting structured technique information from papers.

    Uses Gemini for rich extraction when available, with heuristic fallback.
    """

    EXTRACTION_PROMPT = """Analyze this AI/ML research paper and extract structured technique information.

Title: {title}
Abstract: {abstract}

Extract the following in JSON format:

1. techniques: List of techniques/methods used or introduced. For each:
   - name: The technique name (e.g., "LoRA", "Flash Attention")
   - category: Category (e.g., "fine-tuning", "attention", "normalization", "optimization")
   - technique_type: Type (architecture, training, data, evaluation)
   - is_primary: true if this is the main contribution
   - related_techniques: List of related/similar techniques
   - description: Brief description (1 sentence)

2. architecture_type: Main architecture type (transformer, cnn, diffusion, rnn, hybrid, other)

3. task_domains: List of application domains (e.g., ["NLP", "vision", "multimodal"])

4. novelty_type: What kind of contribution (method, dataset, analysis, benchmark, survey)

5. key_components: List of key algorithmic/architectural components introduced

Return ONLY valid JSON, no other text:
{{
    "techniques": [...],
    "architecture_type": "...",
    "task_domains": [...],
    "novelty_type": "...",
    "key_components": [...]
}}
"""

    def __init__(self):
        self.llm_available = False
        self.model = None

        try:
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                self.llm_available = True
                self.log_info("Technique extraction service initialized with Gemini")
        except Exception as e:
            self.log_warning(
                "Gemini unavailable for technique extraction, using heuristics",
                error=str(e)
            )

    async def extract_techniques(
        self,
        paper_id: str,
        title: str,
        abstract: str
    ) -> TechniqueExtractionResult:
        """
        Extract techniques from a paper.

        Args:
            paper_id: arXiv paper ID
            title: Paper title
            abstract: Paper abstract

        Returns:
            TechniqueExtractionResult with extracted techniques
        """
        if self.llm_available:
            try:
                return await self._extract_with_llm(paper_id, title, abstract)
            except Exception as e:
                self.log_warning(
                    "LLM extraction failed, falling back to heuristics",
                    error=str(e),
                    paper_id=paper_id
                )

        return self._extract_with_heuristics(paper_id, title, abstract)

    async def batch_extract_techniques(
        self,
        papers: List[Dict[str, Any]],
        concurrency: int = 3
    ) -> Dict[str, TechniqueExtractionResult]:
        """
        Extract techniques from multiple papers.

        Args:
            papers: List of paper dicts with id, title, abstract
            concurrency: Max concurrent extractions

        Returns:
            Dict mapping paper_id to extraction results
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def extract_one(paper: Dict[str, Any]) -> tuple:
            async with semaphore:
                result = await self.extract_techniques(
                    paper_id=paper.get("id", ""),
                    title=paper.get("title", ""),
                    abstract=paper.get("abstract", paper.get("summary", ""))
                )
                # Rate limit for LLM
                if self.llm_available:
                    await asyncio.sleep(0.5)
                return paper.get("id", ""), result

        tasks = [extract_one(p) for p in papers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = {}
        for result in results:
            if isinstance(result, Exception):
                continue
            paper_id, extraction = result
            output[paper_id] = extraction

        return output

    async def _extract_with_llm(
        self,
        paper_id: str,
        title: str,
        abstract: str
    ) -> TechniqueExtractionResult:
        """Extract techniques using Gemini LLM"""

        prompt = self.EXTRACTION_PROMPT.format(title=title, abstract=abstract)

        response = await asyncio.to_thread(
            self.model.generate_content,
            prompt
        )

        # Parse JSON response
        text = response.text.strip()

        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in LLM response")

        data = json.loads(json_match.group())

        # Parse techniques
        techniques = []
        for t in data.get("techniques", []):
            name = t.get("name", "")
            techniques.append(ExtractedTechnique(
                name=name,
                normalized_name=self._normalize_name(name),
                category=t.get("category"),
                technique_type=t.get("technique_type"),
                is_primary=t.get("is_primary", False),
                confidence=0.9,  # High confidence for LLM extraction
                related_techniques=t.get("related_techniques", []),
                description=t.get("description")
            ))

        return TechniqueExtractionResult(
            paper_id=paper_id,
            techniques=techniques,
            architecture_type=data.get("architecture_type"),
            task_domains=data.get("task_domains", []),
            novelty_type=data.get("novelty_type"),
            key_components=data.get("key_components", []),
            extraction_method="llm"
        )

    def _extract_with_heuristics(
        self,
        paper_id: str,
        title: str,
        abstract: str
    ) -> TechniqueExtractionResult:
        """Extract techniques using pattern matching heuristics"""

        text = f"{title} {abstract}".lower()

        techniques: List[ExtractedTechnique] = []
        found_names: Set[str] = set()

        # Match technique patterns
        for technique_key, patterns in TECHNIQUE_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in text:
                    if technique_key not in found_names:
                        found_names.add(technique_key)
                        techniques.append(ExtractedTechnique(
                            name=technique_key.replace("_", " ").title(),
                            normalized_name=technique_key,
                            category=self._infer_category(technique_key),
                            technique_type=self._infer_type(technique_key),
                            is_primary=self._is_likely_primary(pattern, title),
                            confidence=0.7,
                            related_techniques=[],
                            description=None
                        ))
                    break

        # Detect architecture type
        architecture_type = None
        for arch in ["transformer", "diffusion", "cnn", "rnn", "gan", "vae", "moe", "ssm"]:
            if arch in found_names or any(p in text for p in TECHNIQUE_PATTERNS.get(arch, [])):
                architecture_type = arch
                break

        # Detect task domains
        task_domains = []
        for domain, keywords in TASK_DOMAINS.items():
            if any(kw in text for kw in keywords):
                task_domains.append(domain)

        # Infer novelty type
        novelty_type = self._infer_novelty_type(title, abstract)

        # Extract key components from title (often mentioned there)
        key_components = self._extract_key_components(title)

        return TechniqueExtractionResult(
            paper_id=paper_id,
            techniques=techniques,
            architecture_type=architecture_type,
            task_domains=task_domains,
            novelty_type=novelty_type,
            key_components=key_components,
            extraction_method="heuristic"
        )

    def _normalize_name(self, name: str) -> str:
        """Normalize technique name for deduplication"""
        return name.lower().replace(" ", "_").replace("-", "_")

    def _infer_category(self, technique_key: str) -> Optional[str]:
        """Infer technique category from key"""
        categories = {
            "transformer": "architecture",
            "diffusion": "architecture",
            "cnn": "architecture",
            "rnn": "architecture",
            "gan": "architecture",
            "vae": "architecture",
            "moe": "architecture",
            "ssm": "architecture",
            "lora": "fine-tuning",
            "qlora": "fine-tuning",
            "peft": "fine-tuning",
            "distillation": "training",
            "contrastive": "training",
            "rlhf": "training",
            "dpo": "training",
            "layer_norm": "normalization",
            "batch_norm": "normalization",
            "dropout": "regularization",
            "rmsnorm": "normalization",
            "flash_attention": "attention",
            "sparse_attention": "attention",
            "linear_attention": "attention",
            "cross_attention": "attention",
            "adam": "optimization",
            "lion": "optimization",
            "schedule_free": "optimization",
            "warmup": "optimization",
            "cosine_decay": "optimization",
        }
        return categories.get(technique_key)

    def _infer_type(self, technique_key: str) -> Optional[str]:
        """Infer technique type"""
        architecture_keys = {"transformer", "diffusion", "cnn", "rnn", "gan", "vae", "moe", "ssm"}
        training_keys = {"lora", "qlora", "peft", "distillation", "contrastive", "rlhf", "dpo"}
        optimization_keys = {"adam", "lion", "schedule_free", "warmup", "cosine_decay"}

        if technique_key in architecture_keys:
            return "architecture"
        elif technique_key in training_keys:
            return "training"
        elif technique_key in optimization_keys:
            return "optimization"

        return "component"

    def _is_likely_primary(self, pattern: str, title: str) -> bool:
        """Check if technique is likely the primary contribution"""
        return pattern.lower() in title.lower()

    def _infer_novelty_type(self, title: str, abstract: str) -> Optional[str]:
        """Infer what type of contribution this is"""
        text = f"{title} {abstract}".lower()

        if any(kw in text for kw in ["dataset", "benchmark", "corpus", "collection"]):
            if "introduce" in text or "present" in text or "release" in text:
                return "dataset"

        if any(kw in text for kw in ["survey", "review", "overview", "comprehensive study"]):
            return "survey"

        if any(kw in text for kw in ["analysis", "study", "investigate", "empirical"]):
            if "propose" not in text and "introduce" not in text:
                return "analysis"

        if any(kw in text for kw in ["benchmark", "evaluation", "compare", "comparison"]):
            return "benchmark"

        # Default to method for papers introducing new techniques
        return "method"

    def _extract_key_components(self, title: str) -> List[str]:
        """Extract key components mentioned in the title"""
        components = []

        # Look for things in parentheses or after colons
        paren_match = re.findall(r'\(([^)]+)\)', title)
        components.extend(paren_match)

        # Look for acronyms (all caps, 2-6 chars)
        acronyms = re.findall(r'\b([A-Z]{2,6})\b', title)
        components.extend(acronyms)

        return list(set(components))[:5]  # Limit to 5


# Module-level singleton
_technique_extraction_service: Optional[TechniqueExtractionService] = None


def get_technique_extraction_service() -> TechniqueExtractionService:
    """Get or create technique extraction service singleton"""
    global _technique_extraction_service
    if _technique_extraction_service is None:
        _technique_extraction_service = TechniqueExtractionService()
    return _technique_extraction_service
