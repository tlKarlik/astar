import tkinter as tk

from graph import Pos, Graph, Node
from path import Path


class GraphCanvas(tk.Canvas):
    node_min_size: int
    pad: int
    graph: Graph
    path: Path[Node]
    node_color = '#A0A0A0'
    selected_node_color = '#DDDDDD'
    node_outline_color = '#FFFFFF'
    selected_node_outline_color = '#AA1010'

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

    def placeLinks(self):
        for start_node_pos, links in self.graph.links_without_duplicates.items():
            for end_node_pos, weight in links.items():
                # print(start_node_pos, end_node_pos, weight)
                link_line = self.create_line(
                    (2 * start_node_pos.x + 0.5) * self.node_size + self.pad,
                    (2 * start_node_pos.y + 0.5) * self.node_size + self.pad,
                    (2 * end_node_pos.x + 0.5) * self.node_size + self.pad,
                    (2 * end_node_pos.y + 0.5) * self.node_size + self.pad,
                    width=4,
                    fill='#FFAA{0}'.format(hex(255 - int(weight * 255 / 20))[2:4].zfill(2)),
                    tags=(str(start_node_pos).replace(' ', ''), str(end_node_pos).replace(' ', ''), 'line')
                )

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

                link_label_bg = self.create_oval(
                    link_xpos - 0.2 * self.node_size,
                    link_ypos - 0.2 * self.node_size,
                    link_xpos + 0.2 * self.node_size,
                    link_ypos + 0.2 * self.node_size,
                    fill='#FFAA{0}'.format(hex(255 - int(weight * 255 / 20))[2:4].zfill(2)),
                    outline=self.node_outline_color,
                    width=2,
                    tags=(str(start_node_pos).replace(' ', ''), str(end_node_pos).replace(' ', ''), 'weightbg')
                )
                link_label = self.create_text(
                    link_xpos,
                    link_ypos,
                    justify=tk.RIGHT,
                    text=weight,
                    font=('Arial', 15),
                    tags=(str(start_node_pos).replace(' ', ''), str(end_node_pos).replace(' ', ''), 'weight')
                )

    def placeNodes(self):
        for node_pos, node in sorted(self.graph.nodes.items(), key=lambda elem: elem[0]):
            node_ell = self.create_oval(
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
            node_label = self.create_text(
                (2 * node_pos.x + 0.5) * self.node_size + self.pad,
                (2 * node_pos.y + 0.5) * self.node_size + self.pad + 3,
                justify=tk.RIGHT,
                text=node.name,
                font=('Arial', 18),
                tags=(node.name, 'node_label')
            )
            node_value = self.create_text(
                (2 * node_pos.x + 0.5) * self.node_size + self.pad,
                (2 * node_pos.y + 0.5) * self.node_size + self.pad - 20,
                justify=tk.RIGHT,
                text='({})'.format(node.value),
                font=('Arial', 10),
                tags=(repr(node_pos).replace(' ', ''), 'node_value')
            )
            # self.graph_labels[node_pos] = node_label

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

    def updateNodeValues(self):
        for node_value_id in self.find_withtag('node_value'):
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

    def _updateNodes(self, new_node: Pos, old_node: Pos):
        node_ellipse_ids = self.find_withtag('node_ellipse')
        for node_ellipse_id in node_ellipse_ids:
            if repr(new_node).replace(' ', '') in self.gettags(node_ellipse_id):
                self.itemconfig(
                    node_ellipse_id,
                    outline=self.selected_node_outline_color,
                    fill=self.selected_node_color,
                    width=8,
                    activeoutline=self.selected_node_color
                )
            elif repr(old_node).replace(' ', '') in self.gettags(node_ellipse_id):
                self.itemconfig(
                    node_ellipse_id,
                    outline=self.node_outline_color,
                    fill=self.node_color,
                    width=2,
                    activeoutline=self.node_color
                )


