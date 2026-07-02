from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    raw_query: str
    product_type: str = ""
    budget_max: float = 9999.0
    must_haves: list[str] = Field(default_factory=list)
    nice_to_haves: list[str] = Field(default_factory=list)
    sites_to_search: list[str] = Field(default_factory=list)


class ProductCandidate(BaseModel):
    title: str
    price: float
    url: str
    rating: Optional[float] = None
    review_count: Optional[int] = None
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    meets_budget: bool = False
    meets_must_haves: bool = False


class AgentState(BaseModel):
    query: SearchQuery
    raw_results: list[dict[str, Any]] = Field(default_factory=list)
    candidates: list[ProductCandidate] = Field(default_factory=list)
    decision_log: list[dict[str, Any]] = Field(default_factory=list)
    final_recommendation: Optional[ProductCandidate] = None
    runner_up: Optional[ProductCandidate] = None
    synthesis_notes: Optional[str] = None
    confidence: Optional[str] = None
    status: str = "planning"
    error: Optional[str] = None


def state_to_dict(state: AgentState) -> dict[str, Any]:
    if hasattr(state, "model_dump"):
        return state.model_dump()
    return state.dict()
