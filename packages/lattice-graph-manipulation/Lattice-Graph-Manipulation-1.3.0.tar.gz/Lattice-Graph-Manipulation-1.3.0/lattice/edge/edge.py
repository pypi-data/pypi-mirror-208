"""
Edges are the connections between nodes
"""

from typing import Any


class Edge:
    """
    Default edge, requires a source and a destination
    We define a cost and a label, attempting to access them will return nothing
    """
    _data: Any
    _label: str

    def __init__(self, label=''):
        self._data = None
        self._label = label

    def get_data(self) -> Any:
        """Get the data we have stored in the edge"""
        return self._data

    def get_label(self) -> str:
        """Return the label assigned to this edge"""
        return self._label



