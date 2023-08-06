"""
A type of node that requires enrichment of cost and label data
"""
from .edge import Edge


class TraverseEdge(Edge):
    """
    This edge requires that a label and a cost is assigned
    """

    def __init__(self, cost: int, label: str):
        super().__init__()
        self._data = cost
        self._label = label

    def get_cost(self) -> int:
        """Return the assigned cost of the edge"""
        return self.get_data()
