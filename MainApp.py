import logging as log
import tkinter as tk
import sys
from tkinter import messagebox
from tkinter import ttk
from typing import Dict

# import graph
import astar_search
from graph import Graph
from graph_canvas import GraphCanvas

# Logging config
log.basicConfig(level=log.INFO)


# log.basicConfig(level=log.INFO, filename='info.log', )


class MainApp(ttk.Frame):
    node_min_size: int = 70
    canvas_pad: int = 5
    pad: int = 5
    master: tk.Tk
    widgets: Dict
    graph: Graph
    canvas: GraphCanvas

    canvas_bg_color: str = '#FBFBFD'
    max_nodes: int = 15
    min_nodes: int = 2

    def __init__(self, master: tk.Tk):
        ttk.Frame.__init__(self, master)
        self.master = master
        self.master.title("A* Algorithm | Tomas Karlik")
        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.widgets = {}

        style = ttk.Style()
        style.configure('canvas.TFrame', background='#FFFFFF')

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
        if sys.platform.startswith('win32'):
            self.master.state('zoomed')
        else:
            self.master.attributes('-zoomed', True)
        master.geometry(self.geom)

        self.main_frame = ttk.Frame(self, width=4 / 5 * self.master.winfo_width() - 2 * self.pad,
                                    height=self.master.winfo_height() - 2 * self.pad, style='canvas.TFrame')
        self.main_frame.grid(row=0, column=0, sticky='EWNS')
        canvas_yscrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL)
        canvas_yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_xscrollbar = tk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL)
        canvas_xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas_scrollbars = (canvas_xscrollbar, canvas_yscrollbar)

        new_style = ttk.Style()
        new_style.configure('test.TFrame', background='green', padding=self.pad)

        self.tab_control = ttk.Notebook(self)
        self.settings_frame = ttk.Frame(self.tab_control)
        self.settings_frame.pack(fill=tk.BOTH, expand=True)
        self.pathfinding_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(self.settings_frame, text='Settings')
        self.tab_control.add(self.pathfinding_frame, text='Steps Output')
        self.tab_control.grid(row=0, column=1, sticky='EWNS', ipadx=self.pad, ipady=self.pad)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.bindings()
        self._controlsInit()
        self.master.update()

    def _clickXCallback(self):
        """Executes the routine to shut the application."""
        log.info('User exited the app by pressing X')
        self.master.destroy()
        exit()

    def _controlsInit(self):
        # Settings Tab
        # Rows 0 & 1
        self._graphSizeControls()
        # Rows 2
        self.gen_button = tk.Button(
            self.settings_frame,
            text='Generate New Graph',
            command=self._generateGraphCallback
        )
        self.widgets['generate_button'] = self.gen_button
        self.gen_button.grid(row=2, column=0, columnspan=2, padx=self.pad, pady=self.pad, sticky='EW')
        tk.Frame(self.settings_frame, height=1, bg='#AAAAAA').grid(row=3, column=0, columnspan=2, padx=self.pad,
                                                                   pady=[4 * self.pad, 2 * self.pad], sticky='EW')
        # Rows 4-7
        self._startEndNodeControls()
        # Rows 8+
        tk.Frame(self.settings_frame, height=1, bg='#AAAAAA').grid(row=8, column=0, columnspan=2, padx=self.pad,
                                                                   pady=2 * self.pad, sticky='EW')
        self.find_path_button = tk.Button(
            self.settings_frame,
            text='Find Path!',
            command=self._findPathCallback,
            state='disabled'
        )
        self.widgets['find_path_button'] = self.find_path_button
        self.find_path_button.grid(row=11, column=0, columnspan=2, padx=self.pad, pady=self.pad, sticky='EWS')

        # Pathing Tab
        pathing_ybar = tk.Scrollbar(self.pathfinding_frame, orient=tk.VERTICAL)
        pathing_ybar.pack(side=tk.RIGHT, fill=tk.Y, padx=[0, self.pad], pady=self.pad)
        pathing_xbar = tk.Scrollbar(self.pathfinding_frame, orient=tk.HORIZONTAL)
        pathing_xbar.pack(side=tk.BOTTOM, fill=tk.X, padx=self.pad, pady=[0, self.pad])
        self.output_text = tk.Text(
            self.pathfinding_frame,
            font=('Courier', 10),
            wrap=tk.NONE,
            foreground='#BB0000',
            state='disabled',
            width=1,
            height=1
        )
        self.widgets['output_text'] = self.output_text
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=[self.pad, 0], pady=[self.pad, 0])
        pathing_ybar.config(command=self.output_text.yview)
        pathing_xbar.config(command=self.output_text.xview)
        self.output_text.config(yscrollcommand=pathing_ybar.set)
        self.output_text.config(xscrollcommand=pathing_xbar.set)

    def _findPathCallback(self):
        try:
            gp = self.graph
        except AttributeError:
            messagebox.showwarning('Warning', 'Please, generate a graph first.')
            return
        data = astar_search.aStar(gp)
        search_info = ''.join(map(lambda el: el + '\n', data['output_data']))
        print(search_info)
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, search_info)
        self.output_text.config(state='disabled')
        self.output_text.update()

        self.canvas.setBestPath(data['best_path'])

        with open('output/last_search.info', 'w') as search_info_file:
            search_info_file.writelines(search_info)

    def _generateGraphCallback(self):
        # self.graph = graph.testMap()
        try:
            graph_width = int(self.graph_xsize_control.current()) + 2
            graph_height = int(self.graph_ysize_control.current()) + 2
        except ValueError:
            messagebox.showwarning('Warning', 'Choose correct graph size first')
            return
        graph_width = min(self.max_nodes, max(self.min_nodes, graph_width))
        graph_height = min(self.max_nodes, max(self.min_nodes, graph_height))
        self.graph = Graph(graph_width, graph_height)
        self.ordered_nodes = sorted(
            [(node.name, node.pos) for node in self.graph.nodes.values()],
            key=lambda x: x[0].zfill(3)
        )
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
                background=self.canvas_bg_color,
                highlightthickness=0,
            )
            self.canvas.pack(fill=tk.BOTH, expand=tk.YES, padx=self.pad, pady=self.pad)

            self.canvas_scrollbars[0].config(command=self.canvas.xview)
            self.canvas_scrollbars[1].config(command=self.canvas.yview)
            self.canvas.config(xscrollcommand=self.canvas_scrollbars[0].set)
            self.canvas.config(yscrollcommand=self.canvas_scrollbars[1].set)

        self.widgets['node_listbox'].configure(state='normal')
        self.widgets['node_listbox'].delete(0, tk.END)
        self.widgets['node_listbox'].insert(tk.END, *[node_name for node_name, node_pos in self.ordered_nodes])
        self.widgets['find_path_button'].config(state='normal')

    def _graphSizeControls(self):
        self.graph_xsize_label = tk.Label(
            self.settings_frame,
            text='Graph width in # nodes:'
        )
        self.graph_xsize_label.grid(row=0, column=0, padx=self.pad, pady=self.pad)
        self.graph_ysize_label = tk.Label(
            self.settings_frame,
            text='Graph height in # nodes:'
        )
        self.graph_ysize_label.grid(row=0, column=1, padx=self.pad, pady=self.pad)
        self.graph_xsize_control = ttk.Combobox(
            self.settings_frame,
            values=list(range(self.min_nodes, self.max_nodes+1))
        )
        self.graph_xsize_control.current(0)
        self.widgets['xsize_combobox'] = self.graph_xsize_control
        self.graph_xsize_control.grid(row=1, column=0, padx=self.pad, pady=self.pad)
        self.graph_ysize_control = ttk.Combobox(
            self.settings_frame,
            values=list(range(self.min_nodes, self.max_nodes+1))
        )
        self.graph_ysize_control.current(0)
        self.widgets['ysize_combobox'] = self.graph_ysize_control
        self.graph_ysize_control.grid(row=1, column=1, padx=self.pad, pady=self.pad)

    def _setNodeCallback(self, node_type: str):
        try:
            selection = int(self.widgets['node_listbox'].curselection()[0])
        except IndexError:
            messagebox.showwarning('Warning', 'Please, select a node from the list')
            return
        node_pos = self.ordered_nodes[selection][1]
        if node_pos == self.graph.start or node_pos == self.graph.goal:
            messagebox.showwarning('Warning', 'Node already selected as start or goal. Please, pick another node.')
            return
        if node_type == 'start':
            self.canvas.updateStartGoalNodes(new_start=node_pos)
        elif node_type == 'goal':
            self.canvas.updateStartGoalNodes(new_goal=node_pos)
        else:
            raise ValueError('Uknown node_type (got {} instead of "start" or "goal")'.format(node_type))

    def _startEndNodeControls(self):
        self.start_node_label = tk.Label(
            self.settings_frame,
            text='Select start and end nodes:'
        )
        self.start_node_label.grid(row=4, column=0, columnspan=2, padx=self.pad, pady=self.pad)

        listbox_frame = ttk.Frame(self.settings_frame)
        listbox_frame.grid(row=5, column=0, columnspan=2, padx=self.pad, pady=self.pad, sticky='EWNS')

        node_select_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        node_select_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.widgets['node_select_scrollbar'] = node_select_scrollbar
        node_select = tk.Listbox(
            listbox_frame,
            selectmode=tk.SINGLE,
            state='disabled'
        )
        self.widgets['node_listbox'] = node_select
        node_select.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        node_select_scrollbar.config(command=node_select.yview)
        node_select.config(yscrollcommand=node_select_scrollbar.set)

        start_node_button = tk.Button(
            self.settings_frame,
            text='Start Node',
            command=lambda: self._setNodeCallback('start')
        )
        self.widgets['start_node_button'] = start_node_button
        start_node_button.grid(row=6, column=0, sticky='EW', padx=self.pad, pady=self.pad)

        goal_node_button = tk.Button(
            self.settings_frame,
            text='Goal Node',
            command=lambda: self._setNodeCallback('goal')
        )
        self.widgets['goal_node_button'] = goal_node_button
        goal_node_button.grid(row=6, column=1, sticky='EW', padx=self.pad, pady=self.pad)

    def bindings(self):
        """Sets key bindings for the app."""
        self.master.protocol('WM_DELETE_WINDOW', self._clickXCallback)
        # self.master.bind("<Configure>", self.canvas.onResize)
        pass

    def clickExit(self):
        """Executes the routine to shut down the application."""
        log.info('User exited the app by pressing the Exit menu item')
        self.master.destroy()
        exit()

    def toggleState(self, state: str):
        """Toggles the states of interactable widgets stored in self.widgets."""
        state = state if state in ('normal', 'disabled') else 'normal'
        for widget in self.widgets:
            # if isinstance(widget, tk.Label or tk.Frame):
            #     continue
            self.widgets[widget].config(state=state)
            log.debug('State of the widget "{}" was changed to "{}"'.format(widget, state))
        log.info('State of the widgets was changed to "{}"'.format(state))

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


def run():
    root = tk.Tk()
    app = MainApp(root)
    app.mainloop()
    log.debug('Exited the app')


if __name__ == '__main__':
    run()
