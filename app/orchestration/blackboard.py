class Blackboard:
    def __init__(self) -> None:
        self._evidence: list[dict] = []

    def add(self, item: dict) -> None:
        self._evidence.append(item)

    def all(self) -> list[dict]:
        return list(self._evidence)
