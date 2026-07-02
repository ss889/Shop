import functools

from langgraph.graph import END, StateGraph

from agent.nodes.comparator import comparator_node
from agent.nodes.extractor import extractor_node
from agent.nodes.planner import planner_node
from agent.nodes.reviewer import reviewer_node
from agent.nodes.searcher import searcher_node
from agent.nodes.synthesizer import synthesizer_node
from agent.schema import AgentState
from agent.tools.browser import BrowserTool


def route(state: AgentState) -> str:
    if state.status in ("failed", "done"):
        return END
    return state.status


async def run_agent(state: AgentState) -> AgentState:
    browser = BrowserTool()
    await browser.start()
    try:
        graph = StateGraph(AgentState)
        graph.add_node("planning", planner_node)
        graph.add_node("searching", functools.partial(searcher_node, browser=browser))
        graph.add_node("extracting", functools.partial(extractor_node, browser=browser))
        graph.add_node("reviewing", reviewer_node)
        graph.add_node("comparing", comparator_node)
        graph.add_node("synthesizing", synthesizer_node)
        graph.set_entry_point("planning")

        for node in [
            "planning",
            "searching",
            "extracting",
            "reviewing",
            "comparing",
            "synthesizing",
        ]:
            graph.add_conditional_edges(node, route)

        app = graph.compile()
        result = await app.ainvoke(state)
        return result if isinstance(result, AgentState) else AgentState(**result)
    finally:
        await browser.stop()
