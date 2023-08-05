import os

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk, Grid, StringVar

from typing import List, Tuple

from byubit.core import BitHistoryRecord, BitHistoryRenderer, draw_record, determine_figure_size


def print_histories(histories: List[Tuple[str, List[BitHistoryRecord]]]):
    for name, history in histories:
        print(name)
        print('-' * len(name))
        for num, record in enumerate(history):
            print(f"{num}: {record.name}")
        print()


class TextRenderer(BitHistoryRenderer):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def render(self, histories: List[Tuple[str, List[BitHistoryRecord]]]):
        if self.verbose:
            print_histories(histories)

        return all(history[-1].error_message is None for _, history in histories)


class LastFrameRenderer(BitHistoryRenderer):
    """Displays the last frame
    Similar to the <=0.1.6 functionality
    """

    def __init__(self, verbose=False, bwmode=False):
        self.verbose = verbose
        self.bwmode = bwmode

    def render(self, histories: List[Tuple[str, List[BitHistoryRecord]]]):
        if self.verbose:
            print_histories(histories)

        for name, history in histories:
            last_record = history[-1]

            fig, axs = plt.subplots(1, 1, figsize=determine_figure_size(last_record.world.shape))
            ax: plt.Axes = fig.gca()

            draw_record(ax, last_record, bwmode=self.bwmode)
            ax.set_title(name, fontsize=14)
            fig.tight_layout()

            plt.show()

        return all(history[-1].error_message is None for _, history in histories)


class MplCanvas(FigureCanvasTkAgg):

    def __init__(self, parent, figsize=(5, 4), dpi=100):
        self.fig = Figure(figsize=figsize, dpi=dpi)
        self.axes = self.fig.add_axes([0, 0, 1, 1])
        super(MplCanvas, self).__init__(self.fig, master=parent)


class MainWindow(tk.Frame):
    histories: List[Tuple[str, List[BitHistoryRecord]]]
    cur_pos: List[int]

    def __init__(self, parent, histories, verbose=False, *args, **kwargs):
        super(MainWindow, self).__init__(parent, *args, **kwargs)

        self.histories = histories
        self.cur_pos = [len(history) - 1 for _, history in histories]
        self.verbose = verbose
        self.grid_propagate(True)

        has_snapshots = any(
            any(
                event.name.startswith('snapshot')
                for event in history
            )
            for _, history in histories
        )

        # Create the maptlotlib FigureCanvas objects,
        # each which defines a single set of axes as self.axes.
        sizes = [determine_figure_size(history[0].world.shape) for _, history in histories]
        size = (max(x for x, _ in sizes), max(y for _, y in sizes))
        self.canvases = []

        # Add tabs of canvases
        style = ttk.Style(self)
        s = ttk.Style()
        s.configure('TNotebook.Tab', font=('URW Gothic L', '17'))
        style.configure('TNotebook', tabposition='s')

        label_widget = tk.Frame(self)

        # Create messages that we can update
        self.f_and_line_number_var = StringVar()
        self.error_var = StringVar()
        self.f_and_line_number_var.set("")
        self.error_var.set("")

        function_line_label = tk.Label(label_widget,
                         width=60,
                         font=("Arial", 17),
                         padx=25,
                         textvariable=self.f_and_line_number_var)
        function_line_label.bind('<Configure>', lambda e: function_line_label.config(wraplength=function_line_label.winfo_width()))
        function_line_label.grid(row=0, column=0, pady=(0, 0))
        Grid.rowconfigure(label_widget, 0, weight=1)
        Grid.columnconfigure(label_widget, 0, weight=1)

        error_label = tk.Label(label_widget,
                         width=60,
                         font=("Arial", 17),
                         fg="red",
                         padx=25,
                         textvariable = self.error_var)
        error_label.bind('<Configure>', lambda e: error_label.config(wraplength=error_label.winfo_width()))
        error_label.grid(row=1, column=0, pady=(0, 0))
        Grid.rowconfigure(label_widget, 1, weight=1)

        label_widget.grid(row=0, column=0, pady=(0, 0))
        # Grid.rowconfigure(self, 0, weight=1)
        Grid.columnconfigure(self, 0, weight=1)

        tabs = ttk.Notebook(self, style='TNotebook', height=int(size[1] * 100), width=int(size[0] * 100))
        tabs.grid(row=1, column=0, pady=(0, 0))
        Grid.rowconfigure(self, 1, weight=1)

        for index, (name, _) in enumerate(histories):
            tab = ttk.Frame(master=tabs)
            canvas = MplCanvas(
                parent=tab,
                figsize=size,
                dpi=100
            )
            canvas.get_tk_widget().grid(row=0, column=0, pady=(0, 0))
            Grid.rowconfigure(tab, 0, weight=1)
            Grid.columnconfigure(tab, 0, weight=1)
            self.canvases.append(canvas)
            tabs.add(tab, text=f"World {index+1}: {name}")

            self._display_current_record(index)

        # Add buttons
        button_widget = tk.Frame(self)

        # Start
        def start_click():
            which = tabs.index('current')
            self.cur_pos[which] = 0
            self._display_current_record(which)

        start_button = ttk.Button(
            master=button_widget,
            text="<<< First",
            command=start_click,
            padding=0
        )
        start_button.grid(row=2, column=0, sticky="nsew")
        Grid.columnconfigure(button_widget, 0, weight=1)

        # Prev snapshot
        if has_snapshots:
            def prev_snap_click():
                which = tabs.index('current')
                cur_pos = self.cur_pos[which]
                _, tab_histories = self.histories[which]
                snapshots = [
                    pos
                    for pos, event in enumerate(tab_histories[:cur_pos])
                    if event.name.startswith('snapshot')
                ]
                prev_pos = snapshots[-1] if snapshots else 0
                self.cur_pos[which] = prev_pos
                self._display_current_record(which)

            prev_snap_button = ttk.Button(
                master=button_widget,
                text="<< Jump",
                command=prev_snap_click,
                padding=0
            )

            prev_snap_button.grid(row=2, column=1, sticky="nsew")
            Grid.columnconfigure(button_widget, 1, weight=1)

        # Back
        def back_click():
            which = tabs.index('current')
            if self.cur_pos[which] > 0:
                self.cur_pos[which] -= 1
            self._display_current_record(which)

        back_button = ttk.Button(
            master=button_widget,
            text="< Prev",
            command=back_click,
            padding=0
        )
        back_button.grid(row=2, column=2, sticky="nsew")
        Grid.columnconfigure(button_widget, 2, weight=1)

        # Next
        def next_click():
            which = tabs.index("current")
            if self.cur_pos[which] < len(self.histories[which][1]) - 1:
                self.cur_pos[which] += 1
            self._display_current_record(which)

        next_button = ttk.Button(
            master=button_widget,
            text="Next >",
            command=next_click,
            padding=0
        )
        next_button.grid(row=2, column=3, sticky="nsew")
        Grid.columnconfigure(button_widget, 3, weight=1)

        # Next snapshot
        if has_snapshots:
            def next_snap_click():
                which = tabs.index("current")
                cur_pos = self.cur_pos[which]
                _, history = self.histories[which]
                snapshots = [
                    pos + cur_pos + 1
                    for pos, event in enumerate(history[cur_pos + 1:])
                    if event.name.startswith('snapshot')
                ]
                next_pos = snapshots[0] if snapshots else len(history) - 1
                self.cur_pos[which] = next_pos
                self._display_current_record(which)

            next_snap_button = ttk.Button(
                master=button_widget,
                text="Jump >>",
                command=next_snap_click,
                padding=0
            )
            next_snap_button.grid(row=2, column=4, sticky="nsew")
            Grid.columnconfigure(button_widget, 4, weight=1)

        # Last
        def last_click():
            which = tabs.index("current")
            self.cur_pos[which] = len(self.histories[which][1]) - 1
            self._display_current_record(which)

        last_button = ttk.Button(
            master=button_widget,
            text="Last >>>",
            command=last_click,
            padding=0
        )
        last_button.grid(row=2, column=5, sticky="nsew")
        Grid.columnconfigure(button_widget, 5, weight=1)

        button_widget.grid_propagate(True)

        button_widget.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="nsew")

    def _display_current_record(self, which):
        self._display_record(which, self.cur_pos[which], self.histories[which][1][self.cur_pos[which]])

    def _display_record(self, which: int, index: int, record: BitHistoryRecord):
        if self.verbose:
            print(f"{index}: {record.name}")

        self.canvases[which].axes.clear()  # Clear the canvas.

        self.f_and_line_number_var.set(f"{index}: {record.name} [{record.filename} line {record.line_number}]")
        self.error_var.set("" if record.error_message is None else record.error_message)
        draw_record(self.canvases[which].axes, record)

        # Trigger the canvas to update and redraw.
        self.canvases[which].draw()


class AnimatedRenderer(BitHistoryRenderer):
    """Displays the world, step-by-step
    The User can pause the animation, or step forward or backward manually
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def render(self, histories: List[Tuple[str, List[BitHistoryRecord]]]):
        """
        Run TKinter application
        """
        matplotlib.use("TkAgg")

        root = tk.Tk()
        root.title('CS 110 Bit')

        bit_panel = MainWindow(root, histories, self.verbose)
        bit_panel.pack()

        root.protocol('WM_DELETE_WINDOW', root.quit)
        tk.mainloop()

        return all(history[-1].error_message is None for _, history in histories)
