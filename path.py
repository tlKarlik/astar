from __future__ import annotations
from typing import List, TypeVar

from graph import Node


Int_or_Float = TypeVar('Int_or_Float', int, float)


class Path(list):
    length: Int_or_Float
    enabled: bool

    def __init__(self, nodes: List[Node], starting_length: Int_or_Float = 0):
        super(Path, self).__init__(nodes)
        self.length = starting_length
        self.enabled = True

    def __str__(self) -> str:
        sw = {True: '', False: ' (disabled)'}
        path = ''
        for node in self[1:-1]:
            path += '{}, '.format(node.name)
        try:
            return '<Path from {} over {}to {} ({}){}>'.format(
                self[0].name, path, self[-1].name, self.weight, sw[self.enabled]
            )
        except IndexError:
            return '<Empty Path>'

    def __repr__(self) -> str:
        sw = {True: '', False: '(disabled) '}
        path = ''
        for node in self[1:-1]:
            path += '{}x{}, '.format(node.x, node.y)
        return '<{}Path from {}x{} over {}to {}x{}>'.format(
            sw[self.enabled], self[0].x, self[0].y, path, self[-1].x, self[-1].y)

    def __add__(self, rhs: Path) -> Path:
        new_length = self.length + rhs.length
        return Path(list.__add__(self, rhs), new_length)

    def __getitem__(self, item: int) -> Node or List[Node]:
        return list.__getitem__(self, item)

    def appendNode(self, node: Node, added_length: int or float):
        self.length += added_length
        super(Path, self).append(node)

    @property
    def weight(self) -> Int_or_Float:
        value = self[-1].value
        return value + self.length

    @property
    def last_node(self) -> Node:
        return self[-1]

    @property
    def start_node(self) -> Node:
        return self[0]

    @property
    def nodes_traveled(self) -> int:
        return len(self)
