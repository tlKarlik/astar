import random
import string
import logging
from collections import namedtuple
from typing import Dict, Tuple


Pos = namedtuple('Pos', 'x y')


class Node(object):

    def __init__(self, name, x, y, value=None):
        self.name = name
        self.pos = Pos(x, y)
        self.x = x
        self.y = y
        self.value = value

    def __str__(self):
        return '<Node {} at {}x{} with a value {}>'.format(self.name, self.x, self.y, self.value)


class Graph(object):
    """A graph object made up of linked nodes with weighted links."""
    x_size: int
    y_size: int
    start: Tuple[int] or None
    goal: Tuple[int] or None
    nodes: Dict[Pos, Node]
    links: Dict[Pos, Dict[Pos, int]]
    links_without_duplicates: Dict[Pos, Dict[Pos, float]]

    def __init__(self, x_size: int, y_size: int, start: Tuple[int] = None, goal: Tuple[int] = None) -> None:
        logging.info('About to generate a graph of size {}x{}'.format(x_size, y_size))
        self.x_size = x_size
        self.y_size = y_size
        self.start, self.goal = self.genStartNGoal(start, goal)
        logging.info('Start is at {}x{} and the goal is {}x{}'.format(
            self.start.x, self.start.y, self.goal.x, self.goal.y
        ))
        self.nodes = {}
        self.links = {}
        self.genNodes()
        self.genLinks()

    @property
    def size(self):
        return self.x_size * self.y_size

    @property
    def links_without_duplicates(self):
        links_without = {}
        for start_node_pos, links in self.links.items():
            for end_node_pos, weight in links.items():
                if end_node_pos not in links_without.keys():
                    try:
                        links_without[start_node_pos][end_node_pos] = weight
                    except KeyError:
                        links_without[start_node_pos] = {end_node_pos: weight}
        return links_without

    def genStartNGoal(self, start: Tuple[int], goal: Tuple[int]) -> Pos:
        """Generates start and goal positions if they weren't defined, otherwise passes them through.

        The location of a start or a goal is always in one of the corners.

        :rtype: tuple[tuple[int], tuple[int]]
        """
        if start is None:
            x_start = random.choice([0, self.x_size - 1])
            y_start = random.choice([0, self.y_size - 1])
            new_start = Pos(x_start, y_start)
        else:
            new_start = Pos(start[0], start[1])
        if goal is None:
            x_goal = new_start.x
            y_goal = new_start.y
            while x_goal == new_start.x and y_goal == new_start.y:
                x_goal = random.choice([0, self.x_size - 1])
                y_goal = random.choice([0, self.y_size - 1])
            new_goal = Pos(x_goal, y_goal)
        else:
            new_goal = Pos(goal[0], goal[1])
        return new_start, new_goal

    def genNodes(self):
        logging.info('Generating nodes...')
        if self.size > len(string.ascii_uppercase):
            names = list(range(1, self.size + 1))
        else:
            names = string.ascii_uppercase
        for y in range(self.y_size):
            for x in range(self.x_size):
                value = (x - self.goal.x) ** 2 + (y - self.goal.y) ** 2
                # node = Node('{}'.format(names[x + y * self.x_size]), x, y, value)
                self.nodes[Pos(x, y)] = Node('{}'.format(names[x + y * self.x_size]), x, y, value)
                self.links[Pos(x, y)] = {}

    def genLinks(self):
        """Generates links between the nodes.

        For each node in self.nodes, it considers the node to the right, to the lower-right, below, and to the
        lower-left. Based on a set chance, an entry might be created in the self.links dict, which has the form of
        {key == the current node: {value == linked node: link length}}. This specifies where the link starts (the key
        in the dict), where the link ends (individual keys in the sub-dict), and the length of the link (the value
        of the key in the sub-dict).
        """
        logging.info('Generating links...')
        links_no = 0
        # for i in range(self.n_nodes):
        for node_pos in self.nodes:
            # the node to the right
            if node_pos.x + 1 < self.x_size:
                if random.random() > 0.1:
                    right_node_pos = Pos(node_pos.x + 1, node_pos.y)
                    length = random.randint(1, 20)
                    self.links[node_pos][right_node_pos] = length
                    self.links[right_node_pos][node_pos] = length
            # the node to the lower-right
            if node_pos.x + 1 < self.x_size and node_pos.y + 1 < self.y_size:
                if random.random() > 0.8:
                    low_right_node_pos = Pos(node_pos.x + 1, node_pos.y + 1)
                    length = random.randint(1, 20)
                    self.links[node_pos][low_right_node_pos] = length
                    self.links[low_right_node_pos][node_pos] = length
            # the node below
            if node_pos.y + 1 < self.y_size:
                if random.random() > 0.1:
                    below_node_pos = Pos(node_pos.x, node_pos.y + 1)
                    length = random.randint(1, 20)
                    self.links[node_pos][below_node_pos] = length
                    self.links[below_node_pos][node_pos] = length
            # the node to the lower-left
            if node_pos.x - 1 >= 0 and node_pos.y + 1 < self.y_size:
                if random.random() > 0.8:
                    low_left_node_pos = Pos(node_pos.x - 1, node_pos.y + 1)
                    length = random.randint(1, 20)
                    self.links[node_pos][low_left_node_pos] = length
                    self.links[low_left_node_pos][node_pos] = length

    def getLinks(self, *args, **kwargs) -> Dict[Pos, int]:
        """Returns all links of a node specified by its location (e.g. (x=1, y=2) or just (1, 2)).

        :rtype: dict
        """
        pos = self._getPos(*args, **kwargs)
        return self.links[pos]

    def getNode(self, *args, **kwargs) -> Node:
        """Returns a node specified by its location (e.g. (x=1, y=2) or just (1, 2))."""
        pos = self._getPos(*args, **kwargs)
        return self.nodes[pos]

    def _getPos(self, *args, **kwargs) -> Pos:
        try:
            pos = Pos(args[0], args[1])
        except IndexError:
            try:
                pos = Pos(kwargs['x'], kwargs['y'])
            except KeyError:
                try:
                    pos = args[0]
                except IndexError:
                    pos = kwargs['pos']
        return pos

    def setStartNode(self, node_pos: Pos):
        self.start = node_pos

    def setGoalNode(self, node_pos: Pos):
        self.goal = node_pos
        self._updateNodeValues()

    def _updateNodeValues(self):
        for y in range(self.y_size):
            for x in range(self.x_size):
                self.nodes[Pos(x, y)].value = (x - self.goal.x) ** 2 + (y - self.goal.y) ** 2


def switcher_ver(index, lst):
    if lst[index] is None:
        return ''
    return '|'


def diagLinksPair2(index, diag_links):
    """Returns True or False based on whether there is a pair at index of diagonal links present in one graph cell.

    :type index: int
    :type diag_links: list
    """
    index_start = index - index % 2
    index_stop = index_start + 2
    if not any(diag_links[index_start:index_stop]):
        return ' ', ' '
    if all(diag_links[index_start:index_stop]):
        if index % 2 == 1:
            return '/', '\\'
        else:
            return '\\', '/'
    if diag_links[index] is not None:
        if index % 2 == 1:
            return '/', ' '
        else:
            return ' ', '\\'
    if diag_links[index + 1] is not None:
        if index % 2 == 1:
            return '\\', ' '
        else:
            return ' ', '/'


def diagLinksPair(index, diag_links):
    """Returns True or False based on whether there is a pair at index of diagonal links present in one graph cell.

    :type index: int
    :type diag_links: list
    """
    index_start = index - index % 2
    index_stop = index_start + 2
    if not any(diag_links[index_start:index_stop]):
        return '  '
    if all(diag_links[index_start:index_stop]):
        return ' X'
    return max(diag_links[index_start:index_stop])


def testMap():
    nodes = {}
    for x in range(3):
        for y in range(3):
            value = (x - 2) ** 2 + y ** 2
            node = Node('{}'.format(string.ascii_uppercase[x + y * 3]), x, y, value=value)
            nodes[Pos(x, y)] = node
    start = Pos(0, 0)
    goal = Pos(2, 0)
    links = dict()
    links[Pos(0, 0)] = {Pos(1, 0): 5}
    links[Pos(1, 0)] = {Pos(2, 0): 14, Pos(1, 1): 12, Pos(0, 0): 5}
    links[Pos(2, 0)] = {Pos(2, 1): 4, Pos(1, 1): 1, Pos(1, 0): 14}
    links[Pos(0, 1)] = {Pos(0, 2): 6, Pos(1, 1): 1}
    links[Pos(1, 1)] = {Pos(2, 1): 5, Pos(2, 2): 20, Pos(1, 2): 18, Pos(1, 0): 12, Pos(2, 0): 1, Pos(0, 1): 1}
    links[Pos(2, 1)] = {Pos(2, 2): 4, Pos(1, 2): 4, Pos(2, 0): 4, Pos(1, 1): 5}
    links[Pos(0, 2)] = {Pos(1, 2): 11, Pos(0, 1): 6}
    links[Pos(1, 2)] = {Pos(1, 1): 18, Pos(0, 2): 11, Pos(2, 1): 4}
    links[Pos(2, 2)] = {Pos(1, 1): 20, Pos(2, 1): 4}
    new_graph = Graph(3, 3, start=start, goal=goal)
    new_graph.nodes = nodes
    new_graph.links = links
    # print "Start: {} | Goal: {}".format(new_graph.start, new_graph.goal)
    # new_graph.printLinks()
    return new_graph


def testMap2():
    nodes = {}
    for x in range(5):
        for y in range(4):
            value = x ** 2 + y ** 2
            node = Node('{}'.format(string.ascii_uppercase[x + y * 5]), x, y, value=value)
            nodes[Pos(x, y)] = node
    start = Pos(4, 3)
    goal = Pos(0, 0)
    links = dict()
    links[Pos(x=0, y=0)] = {Pos(x=0, y=1): 7, Pos(x=1, y=0): 15}
    links[Pos(x=0, y=1)] = {Pos(x=0, y=0): 7, Pos(x=0, y=2): 16}
    links[Pos(x=0, y=2)] = {Pos(x=0, y=1): 16, Pos(x=1, y=2): 6, Pos(x=0, y=3): 3, Pos(x=1, y=3): 12}
    links[Pos(x=0, y=3)] = {Pos(x=1, y=3): 14, Pos(x=0, y=2): 3}
    links[Pos(x=1, y=0)] = {Pos(x=2, y=0): 8, Pos(x=0, y=0): 15, Pos(x=1, y=1): 14}
    links[Pos(x=1, y=1)] = {Pos(x=1, y=2): 3, Pos(x=2, y=0): 18, Pos(x=1, y=0): 14, Pos(x=2, y=1): 20}
    links[Pos(x=1, y=2)] = {Pos(x=1, y=3): 4, Pos(x=2, y=1): 7, Pos(x=0, y=2): 6, Pos(x=2, y=3): 8, Pos(x=2, y=2): 8,
                            Pos(x=1, y=1): 3}
    links[Pos(x=1, y=3)] = {Pos(x=1, y=2): 4, Pos(x=0, y=3): 14, Pos(x=2, y=3): 10, Pos(x=0, y=2): 12}
    links[Pos(x=2, y=0)] = {Pos(x=3, y=0): 9, Pos(x=1, y=0): 8, Pos(x=3, y=1): 17, Pos(x=1, y=1): 18, Pos(x=2, y=1): 10}
    links[Pos(x=2, y=1)] = {Pos(x=1, y=2): 7, Pos(x=2, y=0): 10, Pos(x=3, y=2): 12, Pos(x=1, y=1): 20,
                            Pos(x=2, y=2): 11}
    links[Pos(x=2, y=2)] = {Pos(x=1, y=2): 8, Pos(x=3, y=2): 9, Pos(x=3, y=1): 3, Pos(x=2, y=3): 9, Pos(x=2, y=1): 11}
    links[Pos(x=2, y=3)] = {Pos(x=1, y=2): 8, Pos(x=1, y=3): 10, Pos(x=3, y=3): 5, Pos(x=2, y=2): 9}
    links[Pos(x=3, y=0)] = {Pos(x=2, y=0): 9, Pos(x=3, y=1): 9, Pos(x=4, y=0): 17}
    links[Pos(x=3, y=1)] = {Pos(x=3, y=0): 9, Pos(x=2, y=0): 17, Pos(x=4, y=1): 12, Pos(x=2, y=2): 3}
    links[Pos(x=3, y=2)] = {Pos(x=3, y=3): 15, Pos(x=2, y=1): 12, Pos(x=2, y=2): 9}
    links[Pos(x=3, y=3)] = {Pos(x=3, y=2): 15, Pos(x=2, y=3): 5, Pos(x=4, y=3): 12}
    links[Pos(x=4, y=0)] = {Pos(x=3, y=0): 17, Pos(x=4, y=1): 12}
    links[Pos(x=4, y=1)] = {Pos(x=4, y=2): 16, Pos(x=3, y=1): 12, Pos(x=4, y=0): 12}
    links[Pos(x=4, y=2)] = {Pos(x=4, y=1): 16, Pos(x=4, y=3): 20}
    links[Pos(x=4, y=3)] = {Pos(x=4, y=2): 20, Pos(x=3, y=3): 12}
    new_graph = Graph(5, 4, start=start, goal=goal)
    new_graph.nodes = nodes
    new_graph.links = links
    # print "Start: {} | Goal: {}".format(new_graph.start, new_graph.goal)
    # new_graph.printLinks()
    return new_graph


def main():
    # nodes = ['a', 'b', 'c', 'd', 'e', 'f']
    custom_map = Graph(3, 3)
    print("Start: {} | Goal: {}".format(custom_map.start, custom_map.goal))
    custom_map.printLinks()
    # for node in sorted(custom_map.nodes.keys()):
    #     print str(custom_map.nodes[node])
    # print '======'
    # for link in sorted(custom_map.links.keys()):
    #     print "Node at {} links to nodes at {} with values {}".format(link, custom_map.links.keys(),
    #                                                                   custom_map.links.values())


if __name__ == "__main__":
    # graph = testMap()
    # graph.export2('test.txt')
    graph2 = Graph(5, 4)
    print(graph2.start, graph2.goal)
    print('-----')
    for node in sorted(graph2.nodes):
        print(node, graph2.nodes[node])
    print('-----')
    for link in sorted(graph2.links):
        print(link, graph2.links[link])
    # for i in range(10):
    #     diagLinksPair(i, [])
