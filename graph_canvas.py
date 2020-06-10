import tkinter as tk
from typing import Dict, List, Sequence

from graph import Pos, Graph, Node


# Path = TypeVar('Path', Iterable, Sized)


class GraphCanvas(tk.Canvas):
    node_min_size: int
    pad: int
    graph: Graph
    path: Sequence[Node]
    link_lines: Dict[Pos, Dict[Pos, int]] = {}
    link_label_bgs: Dict[Pos, Dict[Pos, int]] = {}
    link_labels: Dict[Pos, Dict[Pos, int]] = {}
    node_bgs: Dict[Pos, int] = {}
    node_labels: Dict[Pos, int] = {}
    node_values: Dict[Pos, int] = {}

    node_color = '#A0A0A0'
    selected_node_color = '#DDDDDD'
    node_outline_color = '#FFFFFF'
    selected_node_outline_color = '#AA1010'
    default_outline_width = 2
    default_link_width = 4
    highlight_outline_width = 8

    NODE = 'node'
    LINK = 'link'

    def __init__(self, graph: Graph, node_min_size, pad, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Configure>", self._onResize)
        self.node_min_size = node_min_size
        self.pad = pad
        self.graph = None
        self.aspect_ratio = None
        self.node_size = None
        self.width = None
        self.height = None
        self.path = None
        self.setGraph(graph)

    def _onResize(self, event):
        min_width = (2 * self.graph.x_size - 1) * self.node_min_size
        min_height = (2 * self.graph.y_size - 1) * self.node_min_size

        # if the aspect ratio of the new window is smaller than the aspect ratio of the graph, use width,
        # otherwise use height
        if event.width / event.height < self.aspect_ratio:
            new_width = max(event.width, min_width)
            new_height = new_width / self.aspect_ratio
            scale = new_width / self.width
        else:
            new_height = max(event.height, min_height)
            new_width = self.aspect_ratio * new_height
            scale = new_height / self.height

        self.width, self.height = new_width, new_height
        self.config(width=self.width, height=self.height)
        self.scale("all", 0, 0, scale, scale)
        self.update()

    def _reset(self, target_type: str, **options):
        if target_type == self.NODE:
            self.itemconfig(
                self.node_bgs[options['node_pos']],
                outline=self.node_outline_color,
                fill=self.node_color,
                width=self.default_outline_width,
                activeoutline=self.node_color
            )
        elif target_type == self.LINK:
            try:
                link_line_id = self.link_lines[options['link_start']][options['link_end']]
            except KeyError:
                link_line_id = self.link_lines[options['link_end']][options['link_start']]
            weight = self.graph.links[options['link_start']][options['link_end']]
            self.itemconfig(
                link_line_id,
                width=self.default_link_width,
                fill='#FFAA{0}'.format(hex(255 - int(weight * 255 / 20))[2:4].zfill(2))
            )

    def _highlight(self, target_type: str, **options):
        if target_type == self.NODE:
            self.itemconfig(
                self.node_bgs[options['node_pos']],
                outline=self.selected_node_outline_color,
                fill=self.selected_node_color,
                width=self.highlight_outline_width,
                activeoutline=self.selected_node_color
            )
        elif target_type == self.LINK:
            try:
                link_line_id = self.link_lines[options['link_start']][options['link_end']]
            except KeyError:
                link_line_id = self.link_lines[options['link_end']][options['link_start']]
            self.itemconfig(
                link_line_id,
                fill=self.selected_node_outline_color,
                width=self.highlight_outline_width
            )

    def _updateNodes(self, new_node: Pos, old_node: Pos):
        for node_ellipse_id in self.node_bgs.values():
            if repr(new_node).replace(' ', '') in self.gettags(node_ellipse_id):
                self._highlight(self.NODE, node_pos=new_node)
            elif repr(old_node).replace(' ', '') in self.gettags(node_ellipse_id):
                self._reset(old_node)

    def placeLinks(self):
        self.link_lines.clear()
        for start_node_pos, links in self.graph.links_without_duplicates.items():
            for end_node_pos, weight in links.items():
                # print(start_node_pos, end_node_pos, weight)
                link_line_id = self.create_line(
                    (2 * start_node_pos.x + 0.5) * self.node_size + self.pad,
                    (2 * start_node_pos.y + 0.5) * self.node_size + self.pad,
                    (2 * end_node_pos.x + 0.5) * self.node_size + self.pad,
                    (2 * end_node_pos.y + 0.5) * self.node_size + self.pad,
                    width=self.default_link_width,
                    fill='#FFAA{0}'.format(hex(255 - int(weight * 255 / 20))[2:4].zfill(2)),
                    tags=(str(start_node_pos).replace(' ', ''), str(end_node_pos).replace(' ', ''), 'line')
                )
                try:
                    self.link_lines[start_node_pos][end_node_pos] = link_line_id
                except KeyError:
                    self.link_lines[start_node_pos] = {end_node_pos: link_line_id}

        self.link_label_bgs.clear()
        self.link_labels.clear()
        for start_node_pos, links in self.graph.links_without_duplicates.items():
            for end_node_pos, weight in links.items():
                link_xpos = (2 * start_node_pos.x + 1.5) * self.node_size + self.pad
                link_ypos = (2 * start_node_pos.y + 1.5) * self.node_size + self.pad

                if start_node_pos.x != end_node_pos.x and start_node_pos.y != end_node_pos.y:
                    if end_node_pos.x - start_node_pos.x < 0:
                        link_xpos = (2 * start_node_pos.x - 0.2) * self.node_size + self.pad
                    else:
                        link_xpos = (2 * start_node_pos.x + 1.2) * self.node_size + self.pad
                    link_ypos = (2 * start_node_pos.y + 1.2) * self.node_size + self.pad
                else:
                    if start_node_pos.x != end_node_pos.x:
                        link_ypos = (2 * start_node_pos.y + 0.5) * self.node_size + self.pad
                    if start_node_pos.y != end_node_pos.y:
                        link_xpos = (2 * start_node_pos.x + 0.5) * self.node_size + self.pad

                link_label_bg_id = self.create_oval(
                    link_xpos - 0.2 * self.node_size,
                    link_ypos - 0.2 * self.node_size,
                    link_xpos + 0.2 * self.node_size,
                    link_ypos + 0.2 * self.node_size,
                    fill='#FFAA{0}'.format(hex(255 - int(weight * 255 / 20))[2:4].zfill(2)),
                    outline=self.node_outline_color,
                    width=2,
                    tags=(str(start_node_pos).replace(' ', ''), str(end_node_pos).replace(' ', ''), 'weightbg')
                )
                link_label_id = self.create_text(
                    link_xpos,
                    link_ypos,
                    justify=tk.RIGHT,
                    text=weight,
                    font=('Arial', 15),
                    tags=(str(start_node_pos).replace(' ', ''), str(end_node_pos).replace(' ', ''), 'weight')
                )
                try:
                    self.link_label_bgs[start_node_pos][end_node_pos] = link_label_bg_id
                    self.link_labels[start_node_pos][end_node_pos] = link_label_id
                except KeyError:
                    self.link_label_bgs[start_node_pos] = {end_node_pos: link_label_bg_id}
                    self.link_labels[start_node_pos] = {end_node_pos: link_label_id}

    def placeNodes(self):
        self.node_bgs.clear()
        self.node_labels.clear()
        self.node_values.clear()
        for node_pos, node in sorted(self.graph.nodes.items(), key=lambda elem: elem[0]):
            node_bg_id = self.create_oval(
                2 * node_pos.x * self.node_size + self.pad,
                2 * node_pos.y * self.node_size + self.pad,
                (2 * node_pos.x + 1) * self.node_size + self.pad,
                (2 * node_pos.y + 1) * self.node_size + self.pad,
                fill=self.node_color,
                # outline='#22AA22',
                outline=self.node_outline_color,
                width=2,
                activeoutline=self.node_color,
                tags=(repr(node.pos).replace(' ', ''), 'node_ellipse')
            )
            node_label_id = self.create_text(
                (2 * node_pos.x + 0.5) * self.node_size + self.pad,
                (2 * node_pos.y + 0.5) * self.node_size + self.pad + 3,
                justify=tk.RIGHT,
                text=node.name,
                font=('Arial', 18),
                tags=(node.name, 'node_label')
            )
            node_value_id = self.create_text(
                (2 * node_pos.x + 0.5) * self.node_size + self.pad,
                (2 * node_pos.y + 0.5) * self.node_size + self.pad - 20,
                justify=tk.RIGHT,
                text='({})'.format(node.value),
                font=('Arial', 10),
                tags=(repr(node_pos).replace(' ', ''), 'node_value')
            )
            self.node_bgs[node_pos] = node_bg_id
            self.node_labels[node_pos] = node_label_id
            self.node_values[node_pos] = node_value_id

    def setBestPath(self, best_path: Sequence[Node]):
        if self.path is not None:
            for node in self.path:
                self._reset(node.pos)
        for i in range(len(best_path) - 1):
            self._highlight(self.NODE, node_pos=best_path[i].pos)
            self._highlight(self.LINK, link_start=best_path[i].pos, link_end=best_path[i + 1].pos)
        for node in best_path:
            self._highlight(node.pos)
        self.path = best_path
        self.update()

    def setGraph(self, new_graph: Graph):
        self.graph = new_graph
        self.aspect_ratio = (2 * new_graph.x_size - 1) / (2 * new_graph.y_size - 1)
        self.node_size = max(
            self.node_min_size,
            min(
                int((self.master.winfo_width() - 2 * self.pad) / (2 * self.graph.x_size - 1)),
                int((self.master.winfo_height() - 2 * self.pad) / (2 * self.graph.y_size - 1))
            )
        )
        self.width = (2 * self.graph.x_size - 1) * self.node_size + 2 * self.pad
        self.height = (2 * self.graph.y_size - 1) * self.node_size + 2 * self.pad
        self.configure(width=self.width, height=self.height)
        self.placeLinks()
        self.placeNodes()
        self.updateStartGoalNodes(new_start=self.graph.start, new_goal=self.graph.goal)
        self.update()

    def updateNodes(self, node_positions: List[Pos], **options):
        for option, value in options:
            if option == 'start':
                self._updateNodes(new_node=node_positions, old_node=self.graph.start)
                self.graph.setStartNode(node_positions[0])
            elif option == 'goal':
                self._updateNodes(new_node=node_positions, old_node=self.graph.goal)
                self.graph.setGoalNode(node_positions[0])
                self.updateNodeValues()
            elif option == 'reset':
                for node_pos in node_positions:
                    self._reset(self.node_bgs[node_pos])

    def updateNodeValues(self):
        for node_value_id in self.node_values.values():
            tags = self.gettags(node_value_id)
            if tags[0] == 'node_value':
                pos_tag = tags[1]
            else:
                pos_tag = tags[0]
            self.itemconfig(node_value_id, text='({})'.format(self.graph.nodes[eval(pos_tag)].value))
        self.update()

    def updateStartGoalNodes(self, new_start: Pos = None, new_goal: Pos = None):
        if new_start is not None:
            self._updateNodes(new_start, self.graph.start)
            self.graph.setStartNode(new_start)
        if new_goal is not None:
            self._updateNodes(new_goal, self.graph.goal)
            self.graph.setGoalNode(new_goal)
            self.updateNodeValues()
