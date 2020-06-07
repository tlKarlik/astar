import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging as log
from typing import Dict

import graph
from GraphCanvas import GraphCanvas


# Logging config
log.basicConfig(level=log.INFO)
# log.basicConfig(level=log.INFO, filename='info.log', )


class MainApp(ttk.Frame):
    node_min_size: int = 70
    canvas_pad: int = 5
    pad: int = 5
    master: tk.Tk
    widgets: Dict
    graph: graph.Graph
    canvas: GraphCanvas

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
        self.master.state('zoomed')
        master.geometry(self.geom)

        self.main_frame = ttk.Frame(self, width=4/5*self.master.winfo_width()-2*self.pad,
                                    height=self.master.winfo_height()-2*self.pad)
        self.main_frame.grid(row=0, column=0, sticky='EWNS')
        self.button_frame = ttk.Frame(self, width=1/5*self.master.winfo_width()-2*self.pad,
                                      height=self.master.winfo_height()-2*self.pad)
        self.button_frame.grid(row=0, column=1, sticky='EWNS', ipadx=self.pad, ipady=self.pad)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.bindings()
        self._controlsInit()
        self.master.update()

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

    def _controlsInit(self):
        self._graphSizeControls()
        self._startEndNodeControls()

        self.gen_button = tk.Button(
            self.button_frame,
            text='Generate New Graph',
            command=self._generateGraph
        )
        self.widgets['generate_button'] = self.gen_button
        self.gen_button.grid(row=10, column=0, columnspan=2)

    def _graphSizeControls(self):
        self.graph_xsize_label = tk.Label(
            self.button_frame,
            text='Graph width in # nodes:'
        )
        self.graph_xsize_label.grid(row=0, column=0)
        self.graph_ysize_label = tk.Label(
            self.button_frame,
            text='Graph height in # nodes:'
        )
        self.graph_ysize_label.grid(row=0, column=1)
        self.graph_xsize_control = ttk.Combobox(
            self.button_frame,
            values=list(range(2, 11))
        )
        self.graph_xsize_control.current(0)
        self.widgets['xsize_combobox'] = self.graph_xsize_control
        self.graph_xsize_control.grid(row=1, column=0)
        self.graph_ysize_control = ttk.Combobox(
            self.button_frame,
            values=list(range(2, 11))
        )
        self.graph_ysize_control.current(0)
        self.widgets['ysize_combobox'] = self.graph_ysize_control
        self.graph_ysize_control.grid(row=1, column=1)

    def _startEndNodeControls(self):
        self.start_node_label = tk.Label(
            self.button_frame,
            text='Select start and end nodes:'
        )
        self.start_node_label.grid(row=2, column=0, columnspan=2)

        node_select = tk.Listbox(
            self.button_frame,
            selectmode=tk.SINGLE,
            state='disabled'
        )
        self.widgets['node_listbox'] = node_select
        node_select.grid(row=3, column=0, columnspan=2)

        start_node_button = tk.Button(
            self.button_frame,
            text='Start Node',
            command=lambda: self._setNode('start')
        )
        self.widgets['start_node_button'] = start_node_button
        start_node_button.grid(row=4, column=0, sticky='E')

        goal_node_button = tk.Button(
            self.button_frame,
            text='Goal Node',
            command=lambda: self._setNode('goal')
        )
        self.widgets['goal_node_button'] = goal_node_button
        goal_node_button.grid(row=4, column=1, sticky='W')

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
        self.master.protocol('WM_DELETE_WINDOW', self._clickX)
        # self.master.bind("<Configure>", self.canvas.onResize)
        pass

    def _setNode(self, node_type: str):
        selection = int(self.widgets['node_listbox'].curselection()[0])
        node_pos = self.ordered_nodes[selection][1]
        if node_type == 'start':
            self.graph.setStartNode(node_pos)
        elif node_type == 'goal':
            self.graph.setGoalNode(node_pos)
            self.canvas.updateNodeValues()
        else:
            raise ValueError('Uknown node_type (got {} instead of "start" or "goal")'.format(node_type))

    def _clickX(self):
        """Executes the routine to shut the application."""
        log.info('User exited the app by pressing X')
        self.master.destroy()
        exit()

    def clickExit(self):
        """Executes the routine to shut down the application."""
        log.info('User exited the app by pressing the Exit menu item')
        self.master.destroy()
        exit()

    def _generateGraph(self):
        # self.graph = graph.testMap()
        try:
            graph_width = int(self.graph_xsize_control.current()) + 2
            graph_height = int(self.graph_ysize_control.current()) + 2
        except ValueError:
            messagebox.showwarning('Warning', 'Choose correct graph size first')
            return
        self.graph = graph.Graph(graph_width, graph_height)
        self.ordered_nodes = sorted(
            [(node.name, node.pos) for node in self.graph.nodes.values()],
            key=lambda x: x[0].zfill(3)
        )
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
                width=self.main_frame.winfo_width(),
                height=self.main_frame.winfo_height(),
                highlightthickness=0
            )
            self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.canvas.placeLinks()
        self.canvas.placeNodes()
        self.canvas.addtag_all("all")
        self.canvas.update()

        self.widgets['node_listbox'].configure(state='normal')
        self.widgets['node_listbox'].delete(0, tk.END)
        self.widgets['node_listbox'].insert(tk.END, *[node_name for node_name, node_pos in self.ordered_nodes])


def run():
    root = tk.Tk()
    app = MainApp(root)
    app.mainloop()
    log.debug('Exited the app')


if __name__ == '__main__':
    run()

