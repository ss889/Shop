import anthropic

from agent.schema import AgentState, SearchQuery

PLANNER_TOOL = {
    "name": "plan_search",
    "description": "Extract structured search intent from a natural language query",
    "input_schema": {
        "type": "object",
        "properties": {
            "product_type": {"type": "string"},
            "budget_max": {
                "type": "number",
                "description": "Max price in USD. If not stated, use 9999.",
            },
            "must_haves": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Non-negotiable requirements",
            },
            "nice_to_haves": {
                "type": "array",
                "items": {"type": "string"},
            },
            "sites_to_search": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "2-3 sites appropriate for this product. Use bestbuy.com and "
                    "walmart.com. Do not use amazon.com."
                ),
            },
        },
        "required": [
            "product_type",
            "budget_max",
            "must_haves",
            "nice_to_haves",
            "sites_to_search",
        ],
    },
}


async def planner_node(state: AgentState) -> AgentState:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        tools=[PLANNER_TOOL],
        messages=[
            {
                "role": "user",
                "content": f"Plan a product search for: {state.query.raw_query}",
            }
        ],
    )

    tool_use = next((block for block in response.content if block.type == "tool_use"), None)
    if not tool_use:
        state.status = "failed"
        state.error = "Could not parse search query"
        return state

    plan = tool_use.input
    sites = [site for site in plan["sites_to_search"] if "amazon" not in site.lower()]
    if not sites:
        sites = ["bestbuy.com", "walmart.com"]

    state.query = SearchQuery(
        raw_query=state.query.raw_query,
        product_type=plan["product_type"],
        budget_max=plan["budget_max"],
        must_haves=plan["must_haves"],
        nice_to_haves=plan["nice_to_haves"],
        sites_to_search=sites,
    )
    state.status = "searching"
    state.decision_log.append(
        {
            "node": "planner",
            "decision": f"Searching {sites} for {plan['product_type']}",
            "reasoning": (
                f"Budget: ${plan['budget_max']} | Must-haves: {plan['must_haves']}"
            ),
        }
    )
    return state
