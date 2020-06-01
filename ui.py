import tkinter as tk
from tkinter import ttk
import logging as log

import graph


# Logging config
log.basicConfig(level=log.INFO)
# log.basicConfig(level=log.INFO, filename='info.log', )





class MainApp(ttk.Frame):
    node_min_size = 70
    canvas_pad = 5
    pad = 5

    def __init__(self, master: tk.Tk):
        ttk.Frame.__init__(self, master)
        self.master = master
        self.master.title("A* Algorithm | Tomas Karlik")
        self.grid()
        self.widgets = {}

        self.graph = None
        self.canvas = None

        self.geom_size = (
            max(int((self.master.winfo_screenwidth() - self.master.winfo_reqwidth()) / 2 - 100), 700),
            max(int((self.master.winfo_screenheight() - self.master.winfo_reqheight()) / 3 - 70), 700)
        )
        self.geom_pos = (
            int((self.master.winfo_screenwidth() - self.geom_size[0]) / 2),
            int((self.master.winfo_screenheight() - self.geom_size[1]) / 3)
        )
        self.geom = '{}x{}+{}+{}'.format(*self.geom_size, *self.geom_pos)
        # self.master.attributes('-fullscreen', True)
        self.master.state('zoomed')
        master.geometry(self.geom)
        self.master.update()

        self.bindings()

        style = ttk.Style()
        style.configure('Kim.TFrame', background='red')
        style.configure('Tot.TFrame', background='blue')

        self.main_frame = ttk.Frame(self, width=4/5*self.master.winfo_width()-2*self.pad,
                                    height=self.master.winfo_height()-2*self.pad, style='Kim.TFrame')
        self.main_frame.grid(row=0, column=0, columnspan=4, padx=self.pad, pady=self.pad)

        self.button_frame = ttk.Frame(self, width=1/5*self.master.winfo_width()-2*self.pad,
                                      height=self.master.winfo_height()-2*self.pad, style='Tot.TFrame')
        self.button_frame.grid(row=0, column=4, padx=self.pad, pady=self.pad)

        self.gen_button = tk.Button(
            self.button_frame,
            text='Generuj mapu',
            command=self.generateGraph
        )
        self.gen_button.pack(side=tk.BOTTOM)

    @property
    def x_grid(self):
        try:
            return 2 * self.graph.x_size - 1
        except AttributeError:
            return 0

    @property
    def y_grid(self):
        try:
            return 2 * self.graph.y_size - 1
        except AttributeError:
            return 0

    def toggleState(self, state: str):
        """Toggles the states of interactable widgets stored in self.widgets."""
        state = state if state in ('normal', 'disabled') else 'normal'
        for widget in self.widgets:
            # if isinstance(widget, tk.Label or tk.Frame):
            #     continue
            self.widgets[widget].config(state=state)
            log.debug('State of the widget "{}" was changed to "{}"'.format(widget, state))
        log.info('State of the widgets was changed to "{}"'.format(state))

    def bindings(self):
        """Sets key bindings for the app."""
        self.master.protocol('WM_DELETE_WINDOW', self.clickX)
        pass

    def clickX(self):
        """Executes the routine to shut the application."""
        log.info('User exited the app by pressing X')
        self.master.destroy()
        exit()

    def clickExit(self):
        """Executes the routine to shut down the application."""
        log.info('User exited the app by pressing the Exit menu item')
        self.master.destroy()
        exit()

    def generateGraph(self):
        # self.graph = graph.testMap()
        self.graph = graph.Graph(2, 2)
        # self.graph_labels = {}
        try:
            self.canvas.delete(tk.ALL)
            self.canvas.destroy()
        except AttributeError:
            pass

        self.canvas = GraphCanvas(
            self.graph,
            self.node_min_size,
            self.canvas_pad,
            self.main_frame,
            width=4 / 5 * self.master.winfo_width() - 2 * self.pad,
            height=self.master.winfo_height() - 2 * self.pad
            # width=self.x_grid * self.node_min_size + 2 * self.canvas_pad,
            # height=self.x_grid * self.node_min_size + 2 * self.canvas_pad
        )
        self.canvas.pack()
        self.canvas.placeLinks()
        self.canvas.placeNodes()


class GraphCanvas(tk.Canvas):

    def __init__(self, graph: graph.Graph, node_min_size, pad, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = graph
        self.node_min_size = max(
            node_min_size,
            min(
                int((kwargs['width'] - 2 * pad) / (2 * graph.x_size - 1)),
                int((kwargs['height'] - 2 * pad) / (2 * graph.y_size - 1))
            )
        )
        self.pad = pad

    def placeLinks(self):
        for start_node_pos, links in self.graph.links_without_duplicates.items():
            for end_node_pos, weight in links.items():
                # print(start_node_pos, end_node_pos, weight)
                link_line = self.create_line(
                    (2 * start_node_pos.x + 0.5) * self.node_min_size + self.pad,
                    (2 * start_node_pos.y + 0.5) * self.node_min_size + self.pad,
                    (2 * end_node_pos.x + 0.5) * self.node_min_size + self.pad,
                    (2 * end_node_pos.y + 0.5) * self.node_min_size + self.pad,
                    width=4,
                    fill='#FFAA{0}'.format(hex(255 - int(weight * 255 / 20))[2:4].zfill(2)),
                    tags=(str(start_node_pos).replace(' ', ''), str(end_node_pos).replace(' ', ''), 'line')
                )

        for start_node_pos, links in self.graph.links_without_duplicates.items():
            for end_node_pos, weight in links.items():
                link_xpos = (2 * start_node_pos.x + 1.5) * self.node_min_size + self.pad
                link_ypos = (2 * start_node_pos.y + 1.5) * self.node_min_size + self.pad

                if start_node_pos.x != end_node_pos.x and start_node_pos.y != end_node_pos.y:
                    if end_node_pos.x - start_node_pos.x < 0:
                        link_xpos = (2 * start_node_pos.x - 0.2) * self.node_min_size + self.pad
                    else:
                        link_xpos = (2 * start_node_pos.x + 1.2) * self.node_min_size + self.pad
                    link_ypos = (2 * start_node_pos.y + 1.2) * self.node_min_size + self.pad
                else:
                    if start_node_pos.x != end_node_pos.x:
                        link_ypos = (2 * start_node_pos.y + 0.5) * self.node_min_size + self.pad
                    if start_node_pos.y != end_node_pos.y:
                        link_xpos = (2 * start_node_pos.x + 0.5) * self.node_min_size + self.pad

                link_label_bg = self.create_oval(
                    link_xpos - 0.2 * self.node_min_size,
                    link_ypos - 0.2 * self.node_min_size,
                    link_xpos + 0.2 * self.node_min_size,
                    link_ypos + 0.2 * self.node_min_size,
                    fill='#FFAA{0}'.format(hex(255 - int(weight * 255 / 20))[2:4].zfill(2)),
                    outline='SystemButtonFace',
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
                2 * node_pos.x * self.node_min_size + self.pad,
                2 * node_pos.y * self.node_min_size + self.pad,
                (2 * node_pos.x + 1) * self.node_min_size + self.pad,
                (2 * node_pos.y + 1) * self.node_min_size + self.pad,
                fill='#22AA22',
                activefill='#55AA55',
                outline='#22AA22',
                activeoutline='#55AA55',
                tags=node.name
            )
            node_label = self.create_text(
                (2 * node_pos.x + 0.5) * self.node_min_size + self.pad,
                (2 * node_pos.y + 0.5) * self.node_min_size + self.pad,
                justify=tk.RIGHT,
                text=node.name + '-' + str(node.value),
                font=('Arial', 18),
                tags=node.name
            )
            # self.graph_labels[node_pos] = node_label


def run():
    root = tk.Tk()
    app = MainApp(root)
    app.mainloop()
    log.debug('Exited the app')


if __name__ == '__main__':
    run()

