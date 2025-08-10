from typing import Dict, List


class Blackboard:
    def __init__(self) -> None:
        self._evidence: List[Dict] = []

    def add(self, item: Dict) -> None:
        self._evidence.append(item)

    def all(self) -> List[Dict]:
        return list(self._evidence)
