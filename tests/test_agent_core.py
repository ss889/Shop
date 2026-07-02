import asyncio

import pytest

from agent.nodes.comparator import comparator_node
from agent.nodes.reviewer import reviewer_node
from agent.schema import AgentState, ProductCandidate, SearchQuery


def test_comparator_ranks_without_llm_for_single_candidate():
    state = AgentState(
        query=SearchQuery(raw_query="headphones under 200", budget_max=200),
        candidates=[
            ProductCandidate(
                title="Good Headphones",
                price=150,
                url="https://example.com",
                rating=4.5,
                review_count=120,
                meets_budget=True,
                meets_must_haves=True,
            )
        ],
        status="comparing",
    )

    result = comparator_node(state)

    assert result.status == "synthesizing"
    assert result.candidates[0].title == "Good Headphones"
    assert result.decision_log[-1]["node"] == "comparator"


def test_reviewer_eliminates_over_budget_without_llm(monkeypatch):
    class FailingAnthropic:
        def __init__(self):
            raise AssertionError("Anthropic should not be constructed for over-budget candidate")

    monkeypatch.setattr("agent.nodes.reviewer.anthropic.Anthropic", FailingAnthropic)
    state = AgentState(
        query=SearchQuery(raw_query="cheap tablet", budget_max=80, must_haves=["touchscreen"]),
        candidates=[
            ProductCandidate(
                title="Expensive Tablet",
                price=250,
                url="https://example.com",
                meets_budget=False,
            )
        ],
        status="reviewing",
    )

    result = asyncio.run(reviewer_node(state))

    assert result.status == "failed"
    assert "No products found under $80" in result.error
    assert result.decision_log[-1]["node"] == "reviewer"
