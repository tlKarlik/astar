import tkinter as tk
from tkinter import ttk
import logging as log

import graph
from GraphCanvas import GraphCanvas


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
        self.pack(fill=tk.BOTH, expand=tk.YES)
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
                                    height=self.master.winfo_height()-2*self.pad)
        self.main_frame.grid(row=0, column=0, sticky='EWNS')

        self.button_frame = ttk.Frame(self, width=1/5*self.master.winfo_width()-2*self.pad,
                                      height=self.master.winfo_height()-2*self.pad)
        self.button_frame.grid(row=0, column=1, sticky='EWNS', ipadx=self.pad, ipady=self.pad)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.gen_button = tk.Button(
            self.button_frame,
            text='Generuj mapu',
            command=self.generateGraph
        )
        self.gen_button.grid(sticky='NSEW')

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
        # self.master.bind("<Configure>", self.canvas.onResize)
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
        self.graph = graph.Graph(2, 5)
        # self.graph_labels = {}
        try:
            self.canvas.delete(tk.ALL)
            self.canvas.setGraph(self.graph)
        except AttributeError:
            self.canvas = GraphCanvas(
                self.graph,
                self.node_min_size,
                self.canvas_pad,
                self.main_frame,
                # width=4 / 5 * self.master.winfo_width(),
                # height=self.master.winfo_height(),
                width=self.main_frame.winfo_width(),
                height=self.main_frame.winfo_height(),
                background='white',
                highlightthickness=0
                # width=self.x_grid * self.node_min_size + 2 * self.canvas_pad,
                # height=self.x_grid * self.node_min_size + 2 * self.canvas_pad
            )
            self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.canvas.placeLinks()
        self.canvas.placeNodes()
        self.canvas.addtag_all("all")

        self.canvas.update()


def run():
    root = tk.Tk()
    app = MainApp(root)
    app.mainloop()
    log.debug('Exited the app')


if __name__ == '__main__':
    run()

