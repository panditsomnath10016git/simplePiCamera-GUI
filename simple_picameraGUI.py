import os
import json
from time import sleep, strftime
from tkinter import END, Canvas, Entry, Label, Tk, StringVar, DoubleVar, Radiobutton, messagebox
from tkinter.ttk import Button, Frame, Style, Spinbox

# import numpy as np

from picamera import PiCamera

homedir = os.path.expanduser("~")


class App(Tk):
    def __init__(self, **kw) -> None:
        super().__init__(**kw)

        theme = Style()
        self.focus_force()

        # themes ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        theme.theme_use("clam")
        # self.geometry("800x480+300+250")
        self.minsize(410, 300)
        self.title("sPiCameraGUI")

        # For scalebar
        self.lens_zoom = StringVar(self, "5X")
        self.scale_unit = StringVar(self, "um")
        self.fixed_scalebar_len = 50
        self.scalebar_len = self.fixed_scalebar_len
        self.physical_len = DoubleVar(self, 100.0)  # um
        self.scale_bar_font_size = 10

        self.save_dir = os.path.join(homedir, "PiCamCapture", "")
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.image_format = "jpeg"

        self.resolution = (1280, 720)
        self.framerate = 30

        self.create_frames()
        self._camera_init()
        self._set_camera_preview_size()

        self._load_calib_data()
        self._update_fixed_scalebar()
        # self.bind("<Escape>", self._hide_input_window)

    def _camera_init(self):
        while True:
            try:
                self.camera = PiCamera(resolution=self.resolution, framerate=self.framerate)
                break
            except Exception as e:
                if not messagebox.askretrycancel(
                    title="Camera Check", message="Camera not connected"
                ):
                    self.quit()
                    exit()

    def _load_calib_data(self):
        # try loading calib data from calib.json else create initial file
        try:
            with open(self.save_dir + "calib.json", "r") as f:
                self.bars_per_um_per_unit_zoom = json.load(f)
                print("calibration data loaded.")
        except FileNotFoundError:
            messagebox.showwarning(
                "Calibration error", "Scalebar calibration data not found please recalibrate."
            )
            print(
                "calibration file 'calib.json' not found in save dir.\nprocceding with default calibration.."
            )
            # default bars_per_um_per_unit_zoom calculate for initialization
            self.bars_per_um_per_unit_zoom = self.scalebar_len / (
                self.physical_len.get() * int(self.lens_zoom.get()[:-1])
            )  # physical len in um
            self.calib_data = self.bars_per_um_per_unit_zoom

    def create_frames(self):
        self.window = Frame(self.master)
        self.screen_width, self.screen_height = (
            self.winfo_screenwidth(),
            self.winfo_screenheight(),
        )
        self.frame_input_hight = round(self.screen_height / 14)
        self.canvas_width = self.screen_width
        self.canvas_height = self.screen_height - self.frame_input_hight
        self.canvas = Frame(  # changed canvas to frame -maybe better performance
            self.window,
            width=self.canvas_width,
            height=self.canvas_height,
            # bg="white",
        )
        self._input_frame()
        self._calibration_frame()
        self.canvas.grid(column=0, row=0, sticky="nsew")  # pack(anchor="nw", expand=True)
        self.frame_input.grid(column=0, row=1, sticky="nsew")
        self.frame_calib.grid(column=0, row=2, sticky="nsew")
        self.window.pack(fill="both", expand=True)  # grid(column=0, row=0, sticky="nsew")
        self._show_input_window()

    def _input_frame(self):
        self.frame_input = Frame(self.window)
        self.btn_capture = Button(self.frame_input, text="Capture", command=self._capture, width=7)
        img_fname_label = Label(
            self.frame_input,
            text="Save as :",
        )
        img_format = Label(self.frame_input, text=f".{self.image_format}")
        self.ent_img_fname = Entry(self.frame_input, width=30)
        self._set_img_fname()

        # TODO add stop button to stop for capture
        """self.btn_cancel = Button(
            self.frame_input, text="Cancel", command=self._hide_input_window
        )"""
        self.btn_zoom = Spinbox(
            self.frame_input,
            values=("5X", "10X", "20X", "50X", "100X"),
            textvariable=self.lens_zoom,
            width=4,
            command=self._update_fixed_scalebar,
            state="readonly",
        )
        self.scale_msr_show = Label(
            self.frame_input,
            width=5,
            textvariable=self.physical_len,
        )
        self.scale_unit_show = Label(
            self.frame_input,
            width=3,
            textvariable=self.scale_unit,
        )
        # self.zoom_label = Label(self.frame_input, text='X')
        self.scale_msr_show = Label(
            self.frame_input,
            width=5,
            textvariable=self.physical_len,
        )
        self.scale_unit_show = Label(
            self.frame_input,
            width=3,
            textvariable=self.scale_unit,
        )
        self.btn_calib = Button(
            self.frame_input,
            text="Calib",
            width=5,
            command=self._show_calibration_window,
        )
        self.btn_refresh = Button(self.frame_input, text="⟳", width=3, command=self.refresh_camera)
        self.btn_close = Button(self.frame_input, text="Close", width=5, command=self.close_app)

        self.btn_capture.grid(row=0, column=0)
        img_fname_label.grid(row=0, column=1, padx=5)
        self.ent_img_fname.grid(row=0, column=2, padx=0)
        img_format.grid(row=0, column=3, padx=5)
        self.btn_zoom.grid(row=0, column=4, padx=5)
        # self.zoom_label.grid(row=0, column=5, padx=5)

        self.scale_msr_show.grid(row=0, column=5, padx=0)
        self.scale_unit_show.grid(row=0, column=6, padx=0)

        # self.btn_cancel.grid(row=0, column=6, padx=10)
        self.btn_calib.grid(row=0, column=7, padx=2)
        self.btn_refresh.grid(row=0, column=8, padx=2)
        self.btn_close.grid(row=0, column=10, padx=2, sticky="W")

    def _calibration_frame(self):
        # will be visible in screen when calib button pressed in input frame by resizing the canvas
        # it will also disable the input frame to prevent mistouch in screen.
        # OK button will again sent this out of screen and enable input frame
        self.frame_calib = Frame(self.window)
        bar_len_label = Label(
            self.frame_calib,
            text="Scale bar length :",
        )
        self.btn_bar_down = Button(
            self.frame_calib,
            text="▼",
            command=lambda: self._add_scalebar(len=self.scalebar_len - 1),
            width=2,
        )
        self.btn_bar_up = Button(
            self.frame_calib,
            text="▲",
            command=lambda: self._add_scalebar(len=self.scalebar_len + 1),
            width=2,
        )

        label_measured_len = Label(self.frame_calib, text="Measured length :")
        self.ent_measured_len = Entry(self.frame_calib, textvariable=self.physical_len, width=10)

        um_scale = Radiobutton(self.frame_calib, text="um", variable=self.scale_unit, value="um")
        mm_scale = Radiobutton(self.frame_calib, text="mm", variable=self.scale_unit, value="mm")

        self.btn_apply = Button(
            self.frame_calib,
            text="apply",
            width=5,
            command=self._recalculate_scale,
        )
        self.btn_cancel = Button(
            self.frame_calib,
            text="cancel",
            width=6,
            command=self._update_fixed_scalebar,
        )
        self.btn_OK = Button(
            self.frame_calib,
            text="OK",
            width=4,
            command=self._show_input_window,
        )

        bar_len_label.grid(row=0, column=0)
        self.btn_bar_down.grid(row=0, column=1, padx=5)
        self.btn_bar_up.grid(row=0, column=2, padx=5)
        label_measured_len.grid(row=0, column=3, padx=5)
        self.ent_measured_len.grid(row=0, column=4, padx=0)
        um_scale.grid(row=0, column=5, padx=2)
        mm_scale.grid(row=0, column=6, padx=2)
        self.btn_apply.grid(row=0, column=7, padx=5)
        self.btn_cancel.grid(row=0, column=8, padx=5)
        self.btn_OK.grid(row=0, column=9, padx=5)

    def _recalculate_scale(self, *event):
        scale_unit_um = 1
        if self.scale_unit.get() == "mm":
            scale_unit_um = 1000  # 1mm = 1000um

        self.bars_per_um_per_unit_zoom = self.scalebar_len / (
            self.physical_len.get() * scale_unit_um * int(self.lens_zoom.get()[:-1])
        )  # physical len in um

        # Save new calibration data to calib.json
        self.calib_data = self.bars_per_um_per_unit_zoom
        with open(self.save_dir + "calib.json", "w") as f:
            json.dump(self.calib_data, f, indent=2)
            print("calibration data saved!", self.calib_data)

        self._update_fixed_scalebar()

    def _update_fixed_scalebar(self):
        self._add_scalebar(self.fixed_scalebar_len)

    def _update_scalebar(self):
        # TODO dynamic scalebar
        # calculate scale length(with min and max length) to a rounded physical value
        phy_len_values = [1, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
        current_zoom = int(self.lens_zoom.get()[:-1])
        scale_unit_um = 1
        if self.scale_unit.get() == "mm":
            scale_unit_um = 1000  # 1mm = 1000um

        # calcuate bars per length  for the zoom level and update the scalebar
        # according to the zoom set
        min_bar_len = 10
        max_bar_len = 100
        bar_len_per_phy_vals = [
            self.bars_per_um_per_unit_zoom * phy_len * current_zoom for phy_len in phy_len_values
        ]

    def _add_scalebar(self, len, *event):
        self.scalebar_len = len
        # find physical length for the scalebar length
        phy_len = round(
            len / (self.bars_per_um_per_unit_zoom * int(self.lens_zoom.get()[:-1])),
            1,
        )

        # mm unit after 500 um
        if phy_len > 500:
            phy_len /= 1000
            self.scale_unit.set("mm")
        else:
            self.scale_unit.set("um")
        self.physical_len.set(phy_len)

        self.camera.annotate_text_size = self.scale_bar_font_size
        self.camera.annotate_background = True
        self.camera.annotate_text = "_" * len + f"\n{phy_len} {self.scale_unit.get()}"

    """def _add_overlay(self, scale_len=100, scale_wid=50, **kwargs):
        # Create an array representing a image. The shape of
        # the array must be of the form (height, width, color)
        a = np.zeros(
            (self.canvas_width, self.canvas_height, 4), dtype=np.uint8
        )  # black line
        # draw the scale line
        x_offset = 1
        y_offset = 2
        a[
            -y_offset - scale_wid : -y_offset, -x_offset - scale_len : -x_offset, :
        ] = 0xFF
        # Add the overlay directly into layer 3 with transparency;
        # we can omit the size parameter of add_overlay as the
        # size is the same as the camera's resolution
        self.overlay = self.camera.add_overlay(a.tobytes(), layer=3, alpha=64)

    def _remove_overlay(self, overlay):
        self.camera.remove_overlay(overlay)"""

    def _set_camera_preview_size(self, fs=False):
        self.camera.preview_fullscreen = fs
        camera_width = int(1280 * self.canvas_height / 720)
        # x_offset = int((self.canvas_width - camera_width) / 2)
        self.camera.preview_window = (0, 0, camera_width, self.canvas_height)

    def _capture(self, quick=False, *event):
        print("Picture captured!" + self.ent_img_fname.get())
        # capture image(ctrl-s) with default name with timestamp
        if quick:
            self._set_img_fname()

        # TODO if same named image present in directory change the filename.
        # scalebar length added to filename
        self.saved_img_fname = (
            f"{self.ent_img_fname.get()}_{self.physical_len.get()}_{self.scale_unit.get()}.jpeg"
        )
        self.camera.capture(self.save_dir + self.saved_img_fname)
        self._set_img_fname()
        self._show_img_saved()

    def _show_img_saved(self):
        self.camera.annotate_background = True
        self.camera.annotate_text_size = 20
        self.camera.annotate_text = f"Image saved.\n{self.saved_img_fname}"
        sleep(1)
        self._update_fixed_scalebar()

    def _set_img_fname(self):
        self.name_dt = strftime("%Y%m%d%H%M%S")
        self.image_fname = "piCapture" + self.name_dt
        self.ent_img_fname.delete(0, END)
        self.ent_img_fname.insert(0, self.image_fname)
        self.ent_img_fname.focus()

    def _show_input_window(self, *event):
        self.canvas.config(height=(self.screen_height - self.frame_input_hight))
        # self._set_camera_preview_size(fs=False)
        for child in self.frame_input.winfo_children():
            try:
                if child.widgetName != "frame":  # frame has no state, so skip
                    child.configure(state="normal")
            except Exception as e:
                print(e)
        for child in self.frame_calib.winfo_children():
            try:
                if child.widgetName != "frame":  # frame has no state, so skip
                    child.configure(state="disabled")
            except Exception as e:
                print(e)

    def _show_calibration_window(self, *event):
        self.canvas.config(height=(self.screen_height - 2 * self.frame_input_hight))
        # self._set_camera_preview_size(fs=False)
        for child in self.frame_input.winfo_children():
            try:
                if child.widgetName != "frame":  # frame has no state, so skip
                    child.configure(state="disabled")
            except Exception as e:
                print(e)
        for child in self.frame_calib.winfo_children():
            try:
                if child.widgetName != "frame":  # frame has no state, so skip
                    child.configure(state="normal")
            except Exception as e:
                print(e)
        # self.bind("<Escape>", self._show_input_window)

    def refresh_camera(self):
        self.camera.stop_preview()
        self.destroy()
        self.__init__()

    def close_app(self):
        self.camera.stop_preview()
        self.camera.close()
        self.withdraw()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.attributes("-fullscreen", True)
    app.camera.start_preview()
    # self._add_overlay()
    # app.focus_force()
    # app.bind("<Return>", app._capture)
    app.bind("<Control-s>", lambda x: app._capture(quick=True))
    app.bind("<Control-q>", lambda x: app.close_app())
    app.bind("<Control-r>", lambda x: app.refresh_camera())
    app.mainloop()
