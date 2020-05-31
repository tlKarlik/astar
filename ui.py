import tkinter as tk
import logging as log

import graph


# Logging config
log.basicConfig(level=log.INFO)
# log.basicConfig(level=log.INFO, filename='info.log', )


class MainApp(tk.Frame):
    node_min_size = 70
    canvas_pad = 5

    def __init__(self, master: tk.Tk):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title("A* Algorithm | Tomas Karlik")
        self.grid()
        self.widgets = {}

        self.graph = None
        self.canvas = None

        self.pad = 3
        self.x = int((self.master.winfo_screenwidth() - self.master.winfo_reqwidth()) / 2 - 100)
        self.y = int((self.master.winfo_screenheight() - self.master.winfo_reqheight()) / 3 - 70)
        self.geom = '700x700+{}+{}'.format(self.x, self.y)
        master.geometry(self.geom)

        self.bindings()

        # add an area where an image will appear
        self.main_frame = tk.Frame(self, height=650, width=700)
        # self.main_frame.grid(row=0, column=0, pady=5, padx=5)
        self.main_frame.pack(side=tk.TOP, expand=True, ipadx=5, ipady=5)
        self.graph_labels = {}

        # create the frame for the buttons
        self.button_frame = tk.Frame(self)
        # self.button_frame.grid(row=1, column=0, pady=5, padx=5)
        self.button_frame.pack(side=tk.BOTTOM, expand=True)

        # control buttons
        self.generate_button = tk.Button(
            self.button_frame,
            text='Generuj mapu',
            default='active',
            width='10',
            command=self.generateGraph
        )
        self.generate_button.pack(anchor=tk.S)
        self.widgets['generate_button'] = self.generate_button

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
        print(self.main_frame.cget('background'))
        # self.graph = graph.testMap()
        self.graph = graph.Graph(5, 5)
        self.graph_labels = {}
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
            width=self.x_grid * self.node_min_size + 2 * self.canvas_pad,
            height=self.x_grid * self.node_min_size + 2 * self.canvas_pad
        )
        self.canvas.pack()
        self.canvas.placeLinks()
        self.canvas.placeNodes()


class GraphCanvas(tk.Canvas):

    def __init__(self, graph: graph.Graph, node_min_size, pad, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = graph
        self.node_min_size = node_min_size
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
                text=node.name + ', ' + str(node.value),
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

