from agent.schema import AgentState
from agent.tools.browser import BrowserTool


async def searcher_node(state: AgentState, browser: BrowserTool) -> AgentState:
    all_results = []

    for site in state.query.sites_to_search:
        results = await browser.search_site(site, state.query.product_type)
        all_results.extend(results)
        state.decision_log.append(
            {
                "node": "searcher",
                "decision": f"Searched {site}",
                "reasoning": f"Found {len(results)} candidates",
            }
        )

    if not all_results:
        state.status = "failed"
        state.error = (
            "No search results found. The sites may be blocking automated access "
            "or the query returned no results."
        )
        return state

    state.raw_results = all_results
    state.status = "extracting"
    return state
