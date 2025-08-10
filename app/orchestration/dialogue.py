def should_ask_user(ambiguity_score: float, *, threshold: float = 0.6) -> bool:
    return ambiguity_score >= threshold


def make_clarifying_question(gap_description: str) -> str:
    return f"To proceed effectively, could you clarify: {gap_description}?"
