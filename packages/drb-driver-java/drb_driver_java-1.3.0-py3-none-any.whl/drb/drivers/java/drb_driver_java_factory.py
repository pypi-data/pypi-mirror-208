
from drb.drivers.java import DrbJavaBaseNode
from drb.core import DrbNode, DrbFactory


class DrbJavaFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbJavaBaseNode):
            return node
        return DrbJavaBaseNode(base_node=node)
