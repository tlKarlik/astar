import tkinter as tk

import graph


class GraphCanvas(tk.Canvas):
    node_min_size: int
    pad: int
    graph: graph.Graph

    def __init__(self, graph: graph.Graph, node_min_size, pad, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Configure>", self._onResize)
        self.node_min_size = node_min_size
        self.pad = pad
        self.graph = None
        self.aspect_ratio = None
        self.node_size = None
        self.width = None
        self.height = None
        self.setGraph(graph)

    def setGraph(self, new_graph: graph.Graph):
        self.graph = new_graph
        self.aspect_ratio = (2 * new_graph.x_size - 1) / (2 * new_graph.y_size - 1)
        print(self.master.winfo_width(), self.master.winfo_height())
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
                    outline='SystemButtonFace',
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
            # print(node.name)
            node_ell = self.create_oval(
                2 * node_pos.x * self.node_size + self.pad,
                2 * node_pos.y * self.node_size + self.pad,
                (2 * node_pos.x + 1) * self.node_size + self.pad,
                (2 * node_pos.y + 1) * self.node_size + self.pad,
                fill='#22AA22',
                activefill='#55AA55',
                # outline='#22AA22',
                outline='SystemButtonFace',
                width=2,
                activeoutline='#55AA55',
                tags=node.name
            )
            node_label = self.create_text(
                (2 * node_pos.x + 0.5) * self.node_size + self.pad,
                (2 * node_pos.y + 0.5) * self.node_size + self.pad,
                justify=tk.RIGHT,
                text=node.name + '-' + str(node.value),
                font=('Arial', 18),
                tags=node.name
            )
            # self.graph_labels[node_pos] = node_label

    def _onResize(self, event: tk.EventType):
        # TODO: change aspect ratio from square to actual node count
        new_size = min(event.width, event.height)
        if new_size < (2 * max(self.graph.x_size, self.graph.y_size) - 1) * self.node_min_size:
            return
        scale = min(event.width / self.width, event.height / self.height)
        self.width, self.height = new_size, new_size
        self.config(width=self.width, height=self.height)
        self.scale("all", 0, 0, scale, scale)
        self.update()
