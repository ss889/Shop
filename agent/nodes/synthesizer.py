import anthropic

from agent.schema import AgentState

SYNTHESIS_TOOL = {
    "name": "synthesize_recommendation",
    "description": "Produce a final recommendation with honest confidence scoring",
    "input_schema": {
        "type": "object",
        "properties": {
            "recommendation_title": {"type": "string"},
            "recommendation_url": {"type": "string"},
            "why_this_one": {
                "type": "string",
                "description": "2-3 sentences specific to this query, not generic praise",
            },
            "trade_offs": {
                "type": "string",
                "description": "Honest note on what the runner-up offered that the winner does not",
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": (
                    "High = clear winner. Medium = close call. Low = limited options, "
                    "user should verify."
                ),
            },
            "runner_up_title": {"type": ["string", "null"]},
            "runner_up_url": {"type": ["string", "null"]},
        },
        "required": [
            "recommendation_title",
            "recommendation_url",
            "why_this_one",
            "confidence",
        ],
    },
}


async def synthesizer_node(state: AgentState) -> AgentState:
    client = anthropic.Anthropic()
    top = state.candidates[:3]

    summary = "\n".join(
        [
            (
                f"- {candidate.title} (${candidate.price}, Rating: {candidate.rating}/5, "
                f"{candidate.review_count} reviews)\n"
                f"  Pros: {', '.join(candidate.pros[:3])}\n"
                f"  Cons: {', '.join(candidate.cons[:2])}"
            )
            for candidate in top
        ]
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=(
            "You are finalizing a shopping recommendation. Be specific to this query. "
            "Be honest. If confidence is low, say so clearly."
        ),
        tools=[SYNTHESIS_TOOL],
        messages=[
            {
                "role": "user",
                "content": f"""
Query: {state.query.raw_query}
Budget: ${state.query.budget_max}
Must-haves: {state.query.must_haves}

Ranked candidates:
{summary}

Produce a final recommendation.
""",
            }
        ],
    )

    tool_use = next((block for block in response.content if block.type == "tool_use"), None)
    if not tool_use:
        state.status = "failed"
        state.error = "Could not produce final recommendation"
        return state

    rec = tool_use.input
    state.final_recommendation = next(
        (candidate for candidate in state.candidates if candidate.title == rec["recommendation_title"]),
        state.candidates[0],
    )
    state.runner_up = state.candidates[1] if len(state.candidates) > 1 else None
    state.synthesis_notes = rec["why_this_one"]
    state.confidence = rec["confidence"]

    state.decision_log.append(
        {
            "node": "synthesizer",
            "decision": f"Recommended: {rec['recommendation_title']}",
            "reasoning": rec["why_this_one"],
            "confidence": rec["confidence"],
            "trade_offs": rec.get("trade_offs", ""),
        }
    )
    state.status = "done"
    return state
