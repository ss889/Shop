from agent.schema import AgentState


def comparator_node(state: AgentState) -> AgentState:
    budget = state.query.budget_max

    def score(candidate):
        rating_score = (candidate.rating / 5.0) if candidate.rating else 0.3
        review_score = min((candidate.review_count or 0) / 1000, 1.0)
        headroom = (budget - candidate.price) / budget if budget > 0 else 0
        return (0.4 * rating_score) + (0.2 * review_score) + (0.4 * headroom)

    state.candidates.sort(key=score, reverse=True)
    state.decision_log.append(
        {
            "node": "comparator",
            "decision": f"Ranked {len(state.candidates)} candidates",
            "reasoning": (
                f"Top pick: {state.candidates[0].title} at ${state.candidates[0].price}"
            ),
        }
    )
    state.status = "synthesizing"
    return state
