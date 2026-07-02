import anthropic

from agent.schema import AgentState, ProductCandidate
from agent.tools.browser import BrowserTool
from agent.tools.extract import EXTRACTION_TOOL

EXTRACT_SYSTEM = """Extract product data from web page text precisely.
Use sentinel values (-1 for missing numbers, empty lists for missing arrays).
Do not invent values that are not present in the page content."""


async def extractor_node(state: AgentState, browser: BrowserTool) -> AgentState:
    client = anthropic.Anthropic()

    for raw in state.raw_results:
        page_text = await browser.get_page_content(raw["url"])
        if not page_text:
            state.decision_log.append(
                {
                    "node": "extractor",
                    "decision": f"Skipped {raw['url']}",
                    "reasoning": "Page failed to load",
                }
            )
            continue

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            system=EXTRACT_SYSTEM,
            tools=[EXTRACTION_TOOL],
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"URL: {raw['url']}\nTitle hint: {raw['title']}\n\n"
                        f"Page text:\n{page_text}"
                    ),
                }
            ],
        )

        tool_use = next((block for block in response.content if block.type == "tool_use"), None)
        if not tool_use:
            continue

        data = tool_use.input
        price = data["price"] if data["price"] != -1 else None

        if price is None and data["extraction_confidence"] == "low":
            state.decision_log.append(
                {
                    "node": "extractor",
                    "decision": f"Skipped {data['title']}",
                    "reasoning": "Low confidence extraction with no price",
                }
            )
            continue

        candidate = ProductCandidate(
            title=data["title"],
            price=price or 0.0,
            url=raw["url"],
            rating=data["rating"] if data["rating"] != -1 else None,
            review_count=data["review_count"] if data["review_count"] != -1 else None,
            pros=data["pros"],
            cons=data["cons"],
            meets_budget=(price is not None and price <= state.query.budget_max),
            meets_must_haves=False,
        )
        state.candidates.append(candidate)
        state.decision_log.append(
            {
                "node": "extractor",
                "decision": f"Extracted: {candidate.title} at ${candidate.price}",
                "reasoning": (
                    f"Rating: {candidate.rating} | "
                    f"Confidence: {data['extraction_confidence']}"
                ),
            }
        )

    state.raw_results = []
    state.status = "reviewing"
    return state
