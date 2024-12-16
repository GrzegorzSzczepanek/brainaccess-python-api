import time
import yaml
import pathlib
from sys import platform
import subprocess
from sys import exit

import mne
import numpy as np
import PIL
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

from tkinter import *
from tkinter import ttk, font
import tkinter
import PySimpleGUI as sg

matplotlib.use("TKAgg", force=True)

plt.rcParams["axes.prop_cycle"] = plt.cycler("color", plt.cm.tab20.colors)

current_address = pathlib.Path(__file__).parent
logo_address = current_address.joinpath("assets/label-icon-192x192.png")
if platform == "linux" or platform == "linux2":
    bitman_address = current_address.joinpath("assets/favicon.xbm")
else:
    bitman_address = current_address.joinpath("assets/favicon.ico")
imp_img = current_address.joinpath("assets/head_image.png")


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


class UserInterface:
    def __init__(self) -> None:
        # Setup configuration
        cfg_file = pathlib.Path(__file__).parent.joinpath("view.yml")
        with open(cfg_file) as config_yml:
            cfg = yaml.load(config_yml, Loader=yaml.Loader)

        self.set_parameters(cfg)

        # Main application window
        self.root = Tk()
        self.root.title("BrainAccess Viewer")
        self.root.resizable(False, False)
        self.root.minsize(400, 675)

        # Style, fonts, graphics
        tk_style = ttk.Style()
        tk_style.configure("My.TFrame", background="#ffffff")
        label_font = font.Font(
            family="Helvetica", name="LabelFont", size=18, weight="bold", slant="roman"
        )
        textbox_font = font.Font(
            family="Helvetica", name="TextBoxFont", size=12, slant="roman")
        self.second_window_label_font = font.Font(
            family="Helvetica",
            name="StreamLabelFont",
            size=24,
            weight="bold",
            slant="roman",
        )
        self.button_font = font.Font(
            family="Helvetica", name="ButtonFont", size=16, weight="bold", slant="roman"
        )
        logo_img = PhotoImage(file=logo_address)

        if platform == "linux" or platform == "linux2":
            self.root.iconbitmap(f"@{bitman_address}")
        else:
            self.root.iconbitmap(bitman_address)
        space_between_buttons = 6

        # Main window frame
        self.mainframe = ttk.Frame(self.root, padding="35 40 0 0", style="My.TFrame")
        self.mainframe.grid(column=0, row=0, sticky=(W, E, N, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # BrainAccess Favicon Image
        logo_label = ttk.Label(self.mainframe, image=logo_img, background="white")
        logo_label.grid(column=0, row=0, columnspan=2)

        # Brain Access Label
        brand_label = Label(
            self.mainframe,
            text="BrainAccess Viewer",
            pady=20,
            bg="white",
            font=label_font,
        ).grid(column=0, row=1, columnspan=2)

        # Port setting
        self.port_text = Text(self.mainframe, height=1, width=12, font=textbox_font)
        self.port_text.insert(tkinter.END, str(self.port))
        self.port_text.grid(column=0, row=2, pady=space_between_buttons, padx=0)
        port_button = Button(
            self.mainframe, text="Set Port", command=self.set_port,
            fg="#36343E", bg="#EDC900", border=0, height=1, width=8,
            font=self.button_font).grid(column=1, row=2, padx=0, pady=space_between_buttons)

        # Menu buttons
        button1 = self.create_custom_button(
            "Stream", button_func=self.stream_func
        ).grid(column=0, row=3, pady=space_between_buttons, columnspan=2)
        button2 = self.create_custom_button(
            "Plot Impedance", button_func=self.make_impedence_window
        ).grid(column=0, row=4, pady=space_between_buttons, columnspan=2)
        button3 = self.create_custom_button(
            "Plot File", button_func=self.open_file_subproc
        ).grid(column=0, row=5, pady=space_between_buttons, columnspan=2)
        button4 = self.create_custom_button("Quit", button_func=self.close).grid(
            column=0, row=6, pady=space_between_buttons, columnspan=2)

        self.root.mainloop()

    def set_port(self):
        self.port = self.port_text.get("1.0",tkinter.END).strip()

    def set_parameters(self, cfg):
        self.save_imp: bool = cfg["impedances"]["save_imp"]
        self.save_stream: bool = cfg["stream"]["save_stream"]

        self.options: dict
        self.ch_type: str = "eeg"
        self.filter: bool = cfg["stream"]["filter_on"]
        self.filter_low: int = cfg["stream"]["filter_low"]
        self.filter_high: int = cfg["stream"]["filter_high"]
        self.duration: int = cfg["stream"]["duration"]
        self.avg_ref: bool = cfg["stream"]["avg_ref"]
        self.bias: int = cfg["stream"]["bias"]
        self.gain: int = cfg["stream"]["gain"]
        if platform == "linux" or platform == "linux2":
            self.port: str = cfg["hardware"]["linux_port"]
        else:
            self.port: str = cfg["hardware"]["win_port"]
        self.event = None
        self.values = None
        # Deleting empty channels
        self.channel_labels: dict = {int(k): v for k, v in cfg["channel_labels"].items() if v}

    def make_impedence_window(self):
        self.root.withdraw()

        layout = [
            [sg.Canvas(size=(640, 680), key="-CANVAS_IMP-")],
            [sg.Text("Battery:", key="-BAT-", size=(20, 1))],
        ]
        self.win_imp = sg.Window(
            "Impedances", layout, no_titlebar=False, finalize=True, location=(0, 100)
        )

        bg_img = PIL.Image.open(imp_img)
        self.win_imp.bind("<Key-q>", "q")
        canvas_elem = self.win_imp["-CANVAS_IMP-"]
        canvas = canvas_elem.TKCanvas

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.clear()
        ax.axis("off")
        ax.set(facecolor="black")
        fig_agg = draw_figure(canvas, fig)

        from brainaccess.utils import acquisition
        from brainaccess.core.eeg_manager import EEGManager

        if self.save_stream:
            eeg = acquisition.EEG()
        else:
            eeg = acquisition.EEG(mode="roll")
        with EEGManager() as mgr:
            try:
                eeg.setup(
                    mgr,
                    port=self.port,
                    cap=self.channel_labels,
                    zeros_at_start=int(250 * 40),
                    gain = self.gain,
                )
                eeg.start_impedance_measurement()
            except Exception as e:
                print(e)
            else:
                self.win_imp["-BAT-"].update(f"Battery: {eeg.get_battery()} %")
                ll = mne.channels.find_layout(eeg.data.eeg_info)
                nt = time.time()
                while True:
                    t = time.time()
                    if (t - nt) > 5:
                        self.win_imp["-BAT-"].update(f"Battery: {eeg.get_battery()} %")
                        nt = t
                    self.event, self.values = self.win_imp.read(timeout=1000)
                    if self.event in (sg.WINDOW_CLOSED, "Quit", "q"):
                        break

                    imp = eeg.calc_impedances()
                    ax.clear()
                    ax.imshow(bg_img, extent=[0, 1, 0, 1])
                    ax.axis("off")

                    eeg_channel_ids = mne.pick_types(eeg.data.eeg_info, eeg=True)
                    eeg_channel_names = [
                        eeg.data.eeg_info.ch_names[i] for i in eeg_channel_ids
                    ]

                    for idx, name in enumerate(eeg_channel_names):
                        ax.text(
                            (ll.pos[idx, 0]),
                            (ll.pos[idx, 1]),
                            " ".join([name, "\n", str(int(imp[idx])), "\nkOhm"]),
                        )
                    fig_agg.draw()
                eeg.get_mne()
                eeg.stop_impedance_measurement()
                mgr.disconnect()
                if self.save_imp:
                    try:
                        eeg.data.save(f'{time.strftime("%Y%m%d_%H%M")}-impedance-raw.fif')
                    except Exception:
                        print("No data to save")
                eeg.close()
            finally:
                self.win_imp.close()
                self.root.deiconify()

    def create_custom_button(self, text_to_display, button_func=None):
        return Button(
            self.mainframe,
            text=text_to_display,
            command=button_func,
            fg="#36343E",
            bg="#EDC900",
            border=0,
            height=2,
            width=25,
            font=self.button_font,
        )

    def close(self):
        self.root.destroy()
        exit()

    def open_file_subproc(self):
        try:
            address = sg.popup_get_file(
                "Get file", file_types=(("ALL Files", "*.fif"),), no_window=True
            )
            file_to_run = pathlib.Path(__file__).parent.joinpath("plot_file.py")
            subprocess.run([f"python", f"{file_to_run}", f"{address}"])
        except Exception:
            print(Exception)

    def update_stream_bat(self, value):
        self.win_stream["-BAT-"].update(f"{value.level} %")

    def toggle_source(self):
        if self.ch_type == "eeg":
            self.ch_type = ["misc", "stim"]
        else:
            self.ch_type = "eeg"

    def duration_inc(self):
        if self.duration < 18:
            self.duration += 1

    def duration_dec(self):
        if self.duration > 2:
            self.duration -= 1

    def stream_func(self):
        self.root.withdraw()
        layout = [
            [sg.Canvas(size=(1200, 800), key="-CANVAS_STREAM-")],
            [
                sg.Button("Switch source"),
                sg.Button("Increase Duration (+)"),
                sg.Button("Decrease Duration (-)"),
                sg.Text("Battery:", key="-BAT-", size=(20, 1)),
            ],
        ]
        self.win_stream = sg.Window(
            "Stream",
            layout,
            no_titlebar=False,
            finalize=True,
            location=(50, 100),
            resizable=False,
        )

        self.win_stream.bind("<Key-plus>", "Increase Duration (+)")
        self.win_stream.bind("<Key-minus>", "Decrease Duration (-)")
        self.event_dict_stream = {
            "Increase Duration (+)": self.duration_inc,
            "Decrease Duration (-)": self.duration_dec,
        }

        canvas_elem = self.win_stream["-CANVAS_STREAM-"]
        canvas = canvas_elem.TKCanvas

        fig, (ax, ax2) = plt.subplots(
            2, 1, gridspec_kw={"height_ratios": [3, 1]}, figsize=(12, 8)
        )
        ax.clear()
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)
        fig_agg = draw_figure(canvas, fig)

        from brainaccess.utils import acquisition
        from brainaccess.core.eeg_manager import EEGManager

        if self.save_stream:
            eeg = acquisition.EEG()
        else:
            eeg = acquisition.EEG(mode="roll")
        with EEGManager() as mgr:
            try:
                eeg.setup(
                    mgr,
                    port=self.port,
                    cap=self.channel_labels,
                    zeros_at_start=int(250 * 40),
                    bias=[self.bias],
                    gain = self.gain,
                )
                eeg.start_acquisition()
            except Exception as e:
                print(e)
            else:
                self.win_stream["-BAT-"].update(f"Battery: {eeg.get_battery()} %")
                t = time.time()

                while True:
                    nt = time.time()

                    self.event, self.values = self.win_stream.read(timeout=100)
                    if self.event in (sg.WINDOW_CLOSED, "Quit", "q"):
                        break
                    if self.event in ("Switch source"):
                        self.toggle_source()

                    if self.event:
                        if self.event in self.event_dict_stream:
                            action = self.event_dict_stream.get(self.event)
                            action()

                    data = eeg.get_mne(tim=20).copy().pick(self.ch_type)
                    if self.filter:
                        data = data.filter(
                            self.filter_low,
                            self.filter_high,
                            method="fir",
                            verbose=False,
                            picks="all",
                        )
                    data.crop(tmin=data.times[-1] - self.duration)
                    data.apply_function(
                        lambda x: x - np.nanmean(x, axis=0) + 1e-9, picks="all"
                    )
                    if self.avg_ref:
                        data.set_eeg_reference()

                    if nt - t > 5:
                        ax2.clear()
                        data.plot_psd(
                            ax=ax2,
                            show=False,
                            fmin=1,
                            fmax=60,
                            spatial_colors=True,
                            verbose=False,
                            picks="all",
                        )
                        self.win_stream["-BAT-"].update(
                            f"Battery: {eeg.get_battery()} %   "
                        )
                        t = time.time()

                    temp_data = data.get_data()
                    sep = (np.max(np.abs(temp_data))) * np.arange(
                        len(data.ch_names) - 1, -1, -1
                    )

                    ax.clear()
                    ax.plot(data.times, temp_data.T + sep)
                    ax.set_yticks(sep)
                    ax.set_yticklabels(data.ch_names)

                    if self.ch_type == "eeg":
                        fig.suptitle("Electrode stream")
                    else:
                        fig.suptitle("Accelerometer & Digital input stream")

                    rms = np.std(temp_data, axis=1)

                    for idx, itext in enumerate(rms):
                        ax.text(
                            self.duration,
                            sep[idx],
                            f"{itext:.2}",
                            bbox=dict(
                                boxstyle="round",
                                ec=(0.75, 0.75, 0.75),
                                fc=(0.5, 0.5, 0.5),
                            ),
                        )
                    fig_agg.draw()
                eeg.get_mne()
                eeg.stop_acquisition()
                mgr.disconnect()
                if self.save_stream:
                    eeg.data.save(f'{time.strftime("%Y%m%d_%H%M")}-raw.fif')
                eeg.close()
            finally:
                eeg = None
                self.win_stream.close()
                self.root.deiconify()
                self.ch_type = "eeg"


def main():
    ui = UserInterface()


if __name__ == "__main__":
    main()
