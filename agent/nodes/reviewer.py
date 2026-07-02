import anthropic

from agent.schema import AgentState

REVIEWER_TOOL = {
    "name": "evaluate_candidate",
    "description": "Evaluate whether a product meets the search requirements",
    "input_schema": {
        "type": "object",
        "properties": {
            "meets_must_haves": {"type": "boolean"},
            "notes": {"type": "string", "description": "Which must-haves are met or missed"},
            "keep": {"type": "boolean"},
        },
        "required": ["meets_must_haves", "notes", "keep"],
    },
}


async def reviewer_node(state: AgentState) -> AgentState:
    client = None
    kept = []

    for candidate in state.candidates:
        if not candidate.meets_budget:
            state.decision_log.append(
                {
                    "node": "reviewer",
                    "decision": f"Eliminated: {candidate.title}",
                    "reasoning": (
                        f"${candidate.price} exceeds budget of ${state.query.budget_max}"
                    ),
                }
            )
            continue

        if client is None:
            client = anthropic.Anthropic()

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=250,
            tools=[REVIEWER_TOOL],
            messages=[
                {
                    "role": "user",
                    "content": f"""
Must-haves: {state.query.must_haves}
Product: {candidate.title}
Pros: {candidate.pros}
Cons: {candidate.cons}

Does this product meet the must-haves?
""",
                }
            ],
        )

        tool_use = next((block for block in response.content if block.type == "tool_use"), None)
        if not tool_use:
            continue

        evaluation = tool_use.input
        candidate.meets_must_haves = evaluation["meets_must_haves"]

        state.decision_log.append(
            {
                "node": "reviewer",
                "decision": (
                    f"{'Kept' if evaluation['keep'] else 'Eliminated'}: {candidate.title}"
                ),
                "reasoning": evaluation["notes"],
            }
        )

        if evaluation["keep"]:
            kept.append(candidate)

    state.candidates = kept

    if not kept:
        state.status = "failed"
        state.error = (
            f"No products found under ${state.query.budget_max} "
            f"that meet: {state.query.must_haves}. Try relaxing your requirements."
        )
        return state

    state.status = "comparing"
    return state
