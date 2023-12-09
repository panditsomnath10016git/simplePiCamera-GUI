import os
from time import sleep, strftime
from tkinter import END, Canvas, Entry, Label, Tk, StringVar, Radiobutton
from tkinter.ttk import Button, Frame, Style, Spinbox
import numpy as np

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

        self.lens_zoom = "10X"
        self.scale_unit = StringVar("um")

        self.resolution = (1280, 720)
        self.framerate = 30
        self.camera = PiCamera(resolution=self.resolution, framerate=self.framerate)

        self.save_dir = os.path.join(homedir, "PiCamCapture", "")
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.image_format = "jpeg"

        self.create_frames()

        # TODO if camera not found show error dialogue box.
        self.camera.start_preview()
        # self.bind("<Escape>", self._hide_input_window)
        self._set_camera_preview_size()
        # self._add_overlay()
        self._add_scalebar()

    def create_frames(self):
        self.window = Frame(self.master)
        self.screen_width, self.screen_height = (
            self.winfo_screenwidth(),
            self.winfo_screenheight(),
        )
        self.frame_input_hight = 2 * round(self.screen_height / 13)
        self.canvas_width = self.screen_width
        self.canvas_height = self.screen_height - self.frame_input_hight
        self.canvas = Canvas(
            self.window,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white",
        )
        self._input_frame()
        self._calibration_frame()
        self.canvas.grid(
            column=0, row=0, sticky="nsew"
        )  # pack(anchor="nw", expand=True)
        self.frame_input.grid(column=0, row=1, sticky="nsew")
        self.frame_calib.grid(column=0, row=2, sticky="nsew")
        self.window.pack(
            fill="both", expand=True
        )  # grid(column=0, row=0, sticky="nsew")

    def _input_frame(self):
        self.frame_input = Frame(self.window)
        self.btn_capture = Button(
            self.frame_input, text="Capture", command=self._capture, width=7
        )
        img_fname_label = Label(
            self.frame_input,
            text="Save as :",
        )
        img_format = Label(
            self.frame_input,
            text=f".{self.image_format}",
        )
        self.ent_img_fname = Entry(self.frame_input, width=30)
        self._set_img_fname()

        # TODO add stop button to stop for capture
        """self.btn_cancel = Button(
            self.frame_input, text="Cancel", command=self._hide_input_window
        )"""
        self.btn_close = Button(
            self.frame_input, text="Close", width=5, command=self.close_app
        )
        self.btn_zoom = Spinbox(
            self.frame_input,
            values=("10X", "20X", "50X", "100X"),
            textvariable=self.lens_zoom,
            width=4,
            command=self.set_zoom(),
            state="readonly",
        )
        # self.zoom_label = Label(self.frame_input, text='X')
        self.btn_capture.grid(row=0, column=0)

        img_fname_label.grid(row=0, column=1, padx=5)
        self.ent_img_fname.grid(row=0, column=2, padx=0)
        img_format.grid(row=0, column=3, padx=5)
        self.btn_zoom.grid(row=0, column=4, padx=5)
        # self.zoom_label.grid(row=0, column=5, padx=5)

        # self.btn_cancel.grid(row=0, column=6, padx=10)
        self.btn_close.grid(row=0, column=7, padx=30, sticky="W")

    def _calibration_frame(self):
        self.frame_calib = Frame(self.window)
        bar_len_label = Label(
            self.frame_calib,
            text="Scale bar length :",
        )
        self.btn_bar_down = Button(
            self.frame_calib,
            text="↓",
            command=lambda x: self._add_scalebar(len=self.scalebar_len - 1),
            width=2,
        )
        self.btn_bar_up = Button(
            self.frame_calib,
            text="↑",
            command=lambda x: self._add_scalebar(len=self.scalebar_len + 1),
            width=2,
        )

        label_physical_len = Label(
            self.frame_calib,
            text="Physical length :",
        )
        self.ent_actual_len = Entry(self.frame_calib, width=10)

        um_scale = Radiobutton(
            self.frame_calib, text="um", variable=self.scale_unit, value="um"
        )
        mm_scale = Radiobutton(
            self.frame_calib, text="mm", variable=self.scale_unit, value="mm"
        )

        self.btn_apply = Button(
            self.frame_input, text="apply", width=5, command=self._recalculate_scale
        )

        bar_len_label.grid(row=0, column=0)
        self.btn_bar_down.grid(row=0, column=1, padx=5)
        self.btn_bar_up.grid(row=0, column=2, padx=5)
        label_physical_len.grid(row=0, column=3, padx=5)
        self.ent_actual_len.grid(row=0, column=4, padx=0)
        um_scale.grid(row=0, column=5, padx=2)
        mm_scale.grid(row=0, column=6, padx=2)
        self.btn_apply.grid(row=0, column=7, padx=5)

    def _recalculate_scale(self):
        # calculate scale length(with min length 10) to a rounded physical value
        pass

    def set_zoom(self, **kwargs):
        pass

    def _add_scalebar(self, len=20):
        self.scalebar_len = len
        self.camera.annotate_background = True
        self.camera.annotate_text_size = 20
        self.camera.annotate_text = (
            "_" * len + f"\n{self.physical_len} {self.scale_unit}"
        )

    def _calibrate_scale(self):
        # TODO set zoom level , increase the scalebar, set physical length. calculate length per '_'
        # get standard length to show as scalebar.
        pass

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

        # if same named image present in directory change the filename.
        self.saved_img_fname = self.ent_img_fname.get() + ".jpeg"
        self.camera.capture(self.save_dir + self.saved_img_fname)
        self._set_img_fname()
        self._show_img_saved()

    def _show_img_saved(self):
        self.camera.annotate_background = True
        self.camera.annotate_text_size = 20
        self.camera.annotate_text = f"Image saved.\n{self.saved_img_fname}"
        sleep(1)
        self._add_scalebar()

    def _set_img_fname(self):
        self.name_dt = strftime("%Y_%m_%d-%H%M%S")
        self.image_fname = "piCapture" + self.name_dt
        self.ent_img_fname.delete(0, END)
        self.ent_img_fname.insert(0, self.image_fname)
        self.ent_img_fname.focus()

    def _show_input_window(self, *event):
        self.canvas.config(height=(self.screen_height - self.frame_input_hight))
        self._set_camera_preview_size(fs=False)

    def _show_calibration_window(self, *event):
        self.canvas.config(height=(self.screen_height - 2 * self.frame_input_hight))
        self._set_camera_preview_size(fs=False)
        self.bind("<Escape>", self._show_input_window)

    def _hide_input_window(self, *event):
        self.canvas.config(height=(self.screen_height))
        self._set_camera_preview_size(fs=True)
        self.bind("<Escape>", self._show_input_window)

    def close_app(self):
        self.camera.stop_preview()
        self.camera.close()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.attributes("-fullscreen", True)
    # app.focus_force()
    app.bind("<Return>", app._capture)
    app.bind("<Control-s>", lambda x: app._capture(quick=True))
    app.bind("<Control-c>", lambda x: app.close_app())
    app.mainloop()
