"""
A type of node that requires enrichment of cost and label data
"""
from .edge import Edge


class VisualEdge(Edge):
    """
    This is a simple edge that can have a label attached
    It has no expansion on the regular edge as its only relevance is its existence
    To connect edges for a visual representation, this edge must be used
    """
    pass
