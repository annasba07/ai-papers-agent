"""
Pydantic models describing research graph enrichment payloads.

These schemas are used by provider adapters and the ResearchGraphService
to keep contracts explicit while we iterate on data sources.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TechniqueUpsert(BaseModel):
    name: str
    normalized_name: str
    method_type: Optional[str] = None
    emergence_date: Optional[datetime] = None
    maturity_score: float = Field(0.0, ge=0.0, le=10.0)
    description: Optional[str] = None
    embedding: Optional[List[float]] = None
    evidence_source: Optional[str] = None


class TaskUpsert(BaseModel):
    name: str
    taxonomy_path: Optional[str] = None
    modality: Optional[str] = None
    application_domain: Optional[str] = None
    description: Optional[str] = None


class DatasetUpsert(BaseModel):
    name: str
    normalized_name: str
    modality: Optional[str] = None
    sample_count: Optional[int] = None
    license: Optional[str] = None
    maintainer: Optional[str] = None
    url: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata: Optional[dict] = None


class BenchmarkObservation(BaseModel):
    paper_id: str
    task: str
    dataset: str
    metric: str
    value: float
    reported_date: Optional[datetime] = None
    model_name: Optional[str] = None
    model_size: Optional[str] = None
    compute_cost: Optional[str] = None
    evidence_source: str = "external"


class TechniqueRelationshipRecord(BaseModel):
    technique_a_id: int
    technique_b_id: int
    relation_type: str
    weight: Optional[float] = None
    first_seen_paper_id: Optional[str] = None
