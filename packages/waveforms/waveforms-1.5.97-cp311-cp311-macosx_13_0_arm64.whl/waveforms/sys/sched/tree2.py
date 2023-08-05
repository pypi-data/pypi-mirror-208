from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, NamedTuple


class Node(NamedTuple):
    id: int
    parent_id: int
    mask: int
    children_id: list[int]
    data: Any = None

    nodes: dict[int, Node] = {}

    @property
    def parent(self) -> Node:
        return self.nodes[self.parent_id]

    @property
    def children(self) -> list[Node]:
        return [self.nodes[id] for id in self.children_id]


class Tree():

    def __init__(self):
        self.nodes = {}
        self.actived_nodes = set()
        self.waited_nodes = []
        self.mask = 0
        self.nodes[0] = Node(0, 0, 0, [], None, self.nodes)

    def __contains__(self, node: Node) -> bool:
        return node.id in self.nodes

    def valid(self, node: Node) -> bool:
        if node.parent_id not in self.nodes or node.mask & (
                node.parent.mask & self.mask ^ self.mask):
            return False
        return True

    def add_node(self, node, parent=0):
        if node.id in self.nodes:
            return False
        self.nodes[node.id] = node
        self.nodes[parent].children.append(node.id)
        self.deactive_node(parent)
        self.active_node(node.id)
        return True

    def remove_node(self, node_id):
        if node_id not in self.nodes:
            return False
        parent_id = self.nodes[node_id].parent
        for i in self.nodes[node_id].children.copy():
            self.remove_node(i)
        self.deactive_node(node_id)
        if node_id in self.waited_nodes:
            self.waited_nodes.remove(node_id)
        self.nodes[parent_id].children.remove(node_id)
        del self.nodes[node_id]
        if len(self.nodes[parent_id].children) == 0 and parent_id != 0:
            self.waited_nodes.append(parent_id)
        return True

    def deactive_node(self, node_id):
        if node_id not in self.actived_nodes:
            return
        self.actived_nodes.remove(node_id)
        self.mask = self.nodes[node_id].mask & self.mask ^ self.mask

    def active_node(self, node_id):
        self.actived_nodes.add(node_id)
        self.mask |= self.nodes[node_id].mask

    def ask_nodes(self):
        for i in self.waited_nodes.copy():
            if i not in self.nodes:
                self.waited_nodes.remove(i)
                continue
            if not self.nodes[i].mask & self.mask:
                self.waited_nodes.remove(i)
                self.active_node(i)
        return list(self.actived_nodes)
