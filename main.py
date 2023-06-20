from tkinter import (
    END,
    NW,
    W,
    ttk,
    Button,
    Label,
    Entry,
    Menu,
    Text,
    Tk,
    Toplevel,
    filedialog,
)

import time
from datetime import date
import sys
import numpy as np
import os
from sciopy import available_serial_ports, connect_COM_port
from dataclasses import dataclass

from tkinter import messagebox


def action_get_info_dialog():
    m_text = "\
************************\n\
Autor: Jacob Thönes\n\
Date: June 2023\n\
Version: 1.00\n\
Contct: jacob.thoenes@uni-rostock.de \n\
************************"
    messagebox.showinfo(message=m_text, title="Info")


n_el_poss = [16, 32, 48, 64]


@dataclass
class ScioSpecMeasurementConfig:
    """
    burst count: measurements at one instance
    n_el: number of injecting electrodes
    ext_freq: excitational frequency

    """

    burst_count: int
    total_meas_num: int
    n_el: int
    exc_freq: int
    inj_skip: str
    notes: str
    configured: bool


sciospec_measurement_config = ScioSpecMeasurementConfig(
    burst_count=10,
    total_meas_num=10,
    n_el=16,
    exc_freq=10_000,
    inj_skip=0,
    notes="None",
    configured=False,
)


@dataclass
class StoreConfig:
    s_path: str
    save_format: str


store_config = StoreConfig("data/", ".npz")


@dataclass
class ScioSpecDeviceInfo:
    com_port: str
    connection_established: bool


@dataclass
class OperatingSystem:
    system: str
    resolution_width: int
    resolution_height: int


### Constants:
x_0ff = 200
y_0ff = 160
spacer = 20
btn_width = 50
btn_height = 50


# Initializing
sciospec_device_info = ScioSpecDeviceInfo(
    com_port="", connection_established=False
)

available_ports = available_serial_ports()

if available_ports:
    print(f"{available_ports=}")
else:
    print("No serial ports found")
    print("\tFor testing set available_ports to COMFAKE")
    available_ports = ["COMFAKE"]

""" Read resolution and set for visualization. """
import platform
from screeninfo import get_monitors

monitor = get_monitors()

if type(monitor) == list:
    monitor = monitor[0]

print(monitor)

op_system = OperatingSystem(
    system=str(platform.system()),
    resolution_width=int(monitor.width),
    resolution_height=int(monitor.height),
)
print(op_system.system)

###


class Log:
    def __init__(self, app) -> None:
        self.log = Text(app, height=10, width=100)
        self.log.place(x=10, y=590, width=500, height=200)

        self.clear_button = Button(
            app, text="Clear Log", command=self.clear_log
        )
        self.clear_button.place(x=520, y=740, height=50, width=150)

    def write(self, text):
        self.log.insert(END, text)

    def flush(self):
        pass

    def clear_log(self):
        self.log.delete("1.0", END)


class ScioSpecConnect:
    def __init__(self, app) -> None:
        self.com_dropdown_sciospec = ttk.Combobox(values=available_ports)
        self.com_dropdown_sciospec.bind(
            "<<ComboboxSelected>>", self.dropdown_callback
        )
        self.com_dropdown_sciospec.place(
            x=spacer, y=spacer, width=btn_width + spacer, height=btn_height
        )

        self.connect_interact_button = Button(
            app,
            text="Connect ScioSpec",
            bg="#FBC86C",
            state="disabled",
            command=self.connect_interact,
        )
        self.connect_interact_button.place(
            x=3 * spacer + btn_width,
            y=spacer,
            width=x_0ff - spacer,
            height=btn_height,
        )

    def dropdown_callback(self, event=None):
        if event:
            print(f"Selected: {self.com_dropdown_sciospec.get()}")
            sciospec_device_info.com_port = self.com_dropdown_sciospec.get()
            self.connect_interact_button["state"] = "normal"
        else:
            pass

    def connect_interact(self):
        global COM_ScioSpec

        if self.connect_interact_button["text"] == "Disconnect":
            print("Closed serial connection.")
            COM_ScioSpec.close()

        self.connect_interact_button["text"] = "Connecting ..."
        print(
            f"Connecting to {sciospec_device_info.com_port}...",
        )
        try:
            COM_ScioSpec = connect_COM_port(sciospec_device_info.com_port)
            print("Initialization done.")
            self.connect_interact_button["text"] = "Disconnect"
            sciospec_device_info.connection_established = True

            scio_spec_config.open_cnf_window_btn["state"] = "normal"

        except BaseException:
            print("Can not open", sciospec_device_info.com_port)
            sciospec_device_info.connection_established = False
            self.connect_interact_button["text"] = "Connect ScioSpec"


class ScioSpecConfig:
    def __init__(self, app) -> None:
        self.open_cnf_window_btn = Button(
            app,
            text="ScioSpec Config",
            command=self.config_window,
            state="normal",  # Set to disabled, whenn finished programming (TBD)
        )
        self.open_cnf_window_btn.place(
            x=3 * spacer + btn_width,
            y=2 * spacer + btn_height,
            width=x_0ff - spacer,
            height=btn_height,
        )

    def config_window(self):
        self.sciospec_cnf_wndow = Toplevel(app)
        self.sciospec_cnf_wndow.title("Configure ScioSpec")
        self.sciospec_cnf_wndow.geometry("800x400")

        def set_sciospec_settings(self):
            sciospec_measurement_config.burst_count = int(
                entry_burst_count.get()
            )
            sciospec_measurement_config.n_el = int(n_el_dropdown.get())

            sciospec_measurement_config.exc_freq = float(etry_exc_freq.get())
            sciospec_measurement_config.inj_skip = int(inj_skip_dropdown.get())

            notes_inp = entry_note.get("1.0", END)

            sciospec_measurement_config.notes = (
                notes_inp if notes_inp != "Notes\n" else None
            )
            sciospec_measurement_config.configured = True
            if (
                sciospec_device_info.connection_established
                and sciospec_measurement_config.configured
            ):
                send_config.send_cnf_btn["state"] = "normal"

            print(sciospec_measurement_config)
            self.sciospec_cnf_wndow.destroy()

        labels = [
            "Burst count:",
            "Electrodes:",
            "Exc. freq. [Hz]:",
            "Injection skip:",
        ]

        for i in range(len(labels)):
            label = Label(self.sciospec_cnf_wndow, text=labels[i], anchor="w")
            label.place(
                x=0, y=i * btn_width, width=2 * btn_width, height=btn_height
            )

        entry_burst_count = Entry(self.sciospec_cnf_wndow)
        entry_burst_count.place(x=2 * btn_width, y=15, width=3 * btn_width)
        entry_burst_count.insert(0, sciospec_measurement_config.burst_count)

        n_el_dropdown = ttk.Combobox(self.sciospec_cnf_wndow, values=n_el_poss)
        n_el_dropdown.current(
            np.concatenate(
                np.where(
                    np.array(n_el_poss) == sciospec_measurement_config.n_el
                )
            )[0]
        )
        n_el_dropdown.place(
            x=2 * btn_width, y=btn_height + 15, width=3 * btn_width
        )

        etry_exc_freq = Entry(self.sciospec_cnf_wndow)
        etry_exc_freq.place(
            x=2 * btn_width, y=2 * btn_height + 15, width=3 * btn_width
        )
        etry_exc_freq.insert(0, "10000")

        inj_skip_dropdown = ttk.Combobox(
            self.sciospec_cnf_wndow,
            values=[
                ele for ele in np.arange(sciospec_measurement_config.n_el // 2)
            ],
        )
        inj_skip_dropdown.current(0)
        inj_skip_dropdown.place(
            x=2 * btn_width, y=3 * btn_height + 15, width=3 * btn_width
        )

        btn_set_all = Button(
            self.sciospec_cnf_wndow,
            text="Set all selections",
            command=self.set_sciospec_settings,
        )
        btn_set_all.place(
            x=1 * btn_width,
            y=6 * btn_height + 15,
            height=btn_height,
            width=3 * btn_width,
        )

        req_text = Label(
            self.sciospec_cnf_wndow,
            text="Report required settings to:\n jacob.thoenes@uni-rostock.de",
        )
        req_text.place(x=7 * btn_width, y=6 * btn_height + 15)

        entry_note = Text(self.sciospec_cnf_wndow)
        entry_note.place(
            x=6 * btn_width,
            y=15,
            width=4 * btn_width,
            height=5 * btn_height,
            anchor=NW,
        )
        entry_note.insert("1.0", "Notes")


class DataExportConfig:
    def __init__(self, app) -> None:
        self.open_cnf_window_btn = Button(
            app,
            text="Export Config",
            command=self.config_window,
            state="normal",  # Set to disabled, whenn finished programming (TBD)
        )
        self.open_cnf_window_btn.place(
            x=3 * spacer + btn_width,
            y=3 * spacer + 2 * btn_height,
            width=x_0ff - spacer,
            height=btn_height,
        )

    def config_window(self):
        self.export_cnf_wndow = Toplevel(app)
        self.export_cnf_wndow.title("Configure ScioSpec")
        self.export_cnf_wndow.geometry("800x400")

        def open_path_select():
            store_config.s_path = (
                filedialog.askdirectory(title="Select save path") + "/"
            )

        def gen_folder():
            try:
                os.mkdir(store_config.s_path + gen_dir_name.get())
                store_config.s_path = store_config.s_path + gen_dir_name.get()
                print(
                    f"Generated folder {gen_dir_name.get()} at path {store_config.s_path}."
                )

            except BaseException:
                print("Folder already exist.")

        def set_save_config():
            store_config.save_format = file_format.get()
            run_measurement.run_btn["state"] = "normal"
            print(store_config)
            self.export_cnf_wndow.destroy()

        labels = [
            "Savepath",
            "Generate folder",
            "Save file format",
        ]

        for i in range(len(labels)):
            label = Label(self.export_cnf_wndow, text=labels[i], anchor="w")
            label.place(
                x=0, y=i * btn_width, width=3 * btn_width, height=btn_height
            )
        btn_save_path = Button(
            self.export_cnf_wndow, text="Select", command=open_path_select
        )
        btn_save_path.place(x=3 * btn_width, y=15, width=3 * btn_width)

        gen_dir_name = Entry(self.export_cnf_wndow)
        gen_dir_name.place(
            x=3 * btn_width, y=btn_height + 15, width=3 * btn_width
        )
        gen_dir_name.insert(
            0, "meas_" + str(date.today().strftime("%Y-%m-%d"))
        )

        gen_dir_btn = Button(
            self.export_cnf_wndow, text="Generate folder", command=gen_folder
        )
        gen_dir_btn.place(
            x=6 * btn_width + spacer, y=btn_height + 14, width=3 * btn_width
        )

        file_format = ttk.Combobox(
            self.export_cnf_wndow,
            values=[".npz", "hdf5"],
        )
        file_format.current(0)
        file_format.place(
            x=3 * btn_width, y=2 * btn_height + 15, width=3 * btn_width
        )

        btn_set_all = Button(
            self.export_cnf_wndow,
            text="Set all selections",
            command=set_save_config,
        )
        btn_set_all.place(
            x=1 * btn_width,
            y=6 * btn_height + 15,
            height=btn_height,
            width=3 * btn_width,
        )

        req_text = Label(
            self.export_cnf_wndow,
            text="Report required settings to:\n jacob.thoenes@uni-rostock.de",
        )
        req_text.place(x=7 * btn_width, y=6 * btn_height + 15)


class WriteScioSpecConfig:
    def __init__(self, app) -> None:
        self.send_cnf_btn = Button(
            app,
            text="Write Config",
            state="disabled",
            command=self.write_config,
        )
        self.send_cnf_btn.place(
            x=3 * spacer + 5 * btn_width,
            y=2 * spacer + btn_height,
            width=x_0ff - spacer,
            height=btn_height,
        )

    def write_config(self):
        pass


class RunMeasurement:
    def __init__(self, app) -> None:
        self.run_btn = Button(
            app, text="Run", command=self.measure, state="disabled"
        )
        self.run_btn.place(
            x=3 * spacer + btn_width,
            y=450,
            width=x_0ff - spacer,
            height=btn_height,
        )

        # progressbar
        self.progress_bar = ttk.Progressbar(
            app,
            orient="horizontal",
            mode="determinate",
            length=sciospec_measurement_config.total_meas_num,
        )
        self.progress_bar.place(
            x=3 * spacer + btn_width,
            y=450 + btn_height + spacer,
            width=2 * x_0ff,
            height=btn_height,
        )

        self.progress_label = Label(
            app, text=str(int(self.progress_bar["value"])) + "%"
        )
        self.progress_label.place(
            x=3 * spacer + 5 * btn_width,
            y=450,
            width=btn_width,
            height=btn_height,
        )

    def measure(self):
        self.progress_bar["value"] = 0
        for i in range(sciospec_measurement_config.total_meas_num):
            time.sleep(1)
            # TBD: Inser Measurement here
            print(f"{i=}")
            self.progress_bar["value"] += (
                100 / sciospec_measurement_config.total_meas_num
            )
            self.progress_label["text"] = (
                str(int(self.progress_bar["value"])) + "%"
            )
            app.update_idletasks()
            if (
                self.progress_bar["value"]
                == sciospec_measurement_config.total_meas_num * 100
            ):
                messagebox.showinfo(message="The progress completed!")
                self.progress_bar["value"] = 0
        self.progress_bar["value"] = 0


"""Main Init"""
app = Tk()
app.title("ScioSpec Python GUI")
app.configure(background="#1A5175")
app.grid()


try:
    app.iconbitmap("../images/ico_sciopy.ico")
except BaseException:
    print("\t tkinter.TclError: bitmap not defined")

connect_sciospec = ScioSpecConnect(app)
scio_spec_config = ScioSpecConfig(app)
send_config = WriteScioSpecConfig(app)

save_config = DataExportConfig(app)

run_measurement = RunMeasurement(app)


LOG = Log(app)
sys.stdout = LOG


dropdown = Menu(app)
datei_menu = Menu(dropdown, tearoff=0)
help_menu = Menu(dropdown, tearoff=0)

datei_menu.add_separator()
datei_menu.add_command(label="Exit", command=app.quit)
help_menu.add_command(label="Info", command=action_get_info_dialog)
dropdown.add_cascade(label="File", menu=datei_menu)
dropdown.add_cascade(label="Help", menu=help_menu)


app.config(menu=dropdown)
app.geometry("680x800")
app.mainloop()