import os
from time import sleep, strftime
from tkinter import END, Canvas, Entry, Label, Tk
from tkinter.ttk import Button, Frame, Style, Spinbox

from picameraa import PiCamera


homedir = os.path.expanduser("~")


class App(Tk):
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        # for testing without camera
        self.screen_width = 800
        self.screen_height = 480

        theme = Style()
        self.focus_force()

        # themes ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        theme.theme_use("clam")
        # self.geometry("800x480+300+250")
        self.minsize(410, 300)
        self.title("sPiCameraGUI")

        self.lens_zoom = 10

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
        self.bind("<Escape>", self._hide_input_window)
        self._set_camera_preview_size()

    def create_frames(self):
        self.window = Frame(self.master)
        """self.screen_width, self.screen_height = (
            self.winfo_screenwidth(),
            self.winfo_screenheight(),
        )"""
        self.frame_input_hight = round(self.screen_height / 13)
        self.canvas_width = self.screen_width
        self.canvas_height = self.screen_height - self.frame_input_hight
        self.canvas = Canvas(
            self.window,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white",
        )
        self._input_frame()
        self.canvas.grid(
            column=0, row=0, sticky="nsew"
        )  # pack(anchor="nw", expand=True)
        self.frame_input.grid(column=0, row=1, sticky="nsew")
        self.window.pack(
            fill="both", expand=True
        )  # grid(column=0, row=0, sticky="nsew")

    def _input_frame(self):
        self.frame_input = Frame(self.window)
        self.btn_capture = Button(
            self.frame_input, text="Capture", command=self._capture
        )
        img_fname_label = Label(
            self.frame_input,
            text="Save image as :",
        )
        img_format = Label(
            self.frame_input,
            text=f".{self.image_format}",
        )
        self.ent_img_fname = Entry(self.frame_input, width=30)
        self._set_img_fname()

        self.btn_cancel = Button(
            self.frame_input, text="Cancel", command=self._hide_input_window
        )
        self.btn_close = Button(self.frame_input, text="Close", command=self.close_app)
        self.btn_zoom = Spinbox(
            self.frame_input,
            values=("10X", "20X", "50X", "100X"),
            textvariable=self.lens_zoom,
            width=4,
            command=self.set_zoom(),
            state='readonly'
        )
        # self.zoom_label = Label(self.frame_input, text='X')
        self.btn_capture.grid(row=0, column=0)

        img_fname_label.grid(row=0, column=1, padx=5)
        self.ent_img_fname.grid(row=0, column=2, padx=0)
        img_format.grid(row=0, column=3, padx=5)
        self.btn_zoom.grid(row=0, column=4, padx=5)
        # self.zoom_label.grid(row=0, column=5, padx=5)

        self.btn_cancel.grid(row=0, column=6, padx=10)
        self.btn_close.grid(row=0, column=7, padx=30, sticky="W")

    def set_zoom(self, **kwargs):
        pass

    def _set_camera_preview_size(self, fs=False):
        self.camera.preview_fullscreen = fs
        camera_width = int(1280 * self.canvas_height / 720)
        x_offset = int((self.canvas_width - camera_width) / 2)
        self.camera.preview_window = (x_offset, 0, camera_width, self.canvas_height)

    def _capture(self, *event):
        print("Picture captured!" + self.ent_img_fname.get())
        # if in fullscreen mode capture image(ctrl-s) with default name with timestamp
        if self.camera.preview_fullscreen == True:
            self._set_img_fname()

        # if same named image present in directory change the filename.
        self.saved_img_fname = self.ent_img_fname.get() + ".jpeg"
        self.camera.capture(self.save_dir + self.saved_img_fname)
        self._show_img_saved()

    def _show_img_saved(self):
        self.camera.annotate_background = True
        self.camera.annotate_text_size = 20
        self.camera.annotate_text = f"Image saved.\n{self.saved_img_fname}"
        sleep(2)
        self.camera.annotate_text = ""

    def _set_img_fname(self):
        self.name_dt = strftime("%Y_%m_%d-%H%M%S")
        self.image_fname = "piCapture" + self.name_dt
        self.ent_img_fname.delete(0, END)
        self.ent_img_fname.insert(0, self.image_fname)
        self.ent_img_fname.focus()

    def _show_input_window(self, *event):
        self._set_img_fname()
        self.canvas.config(height=(self.screen_height - self.frame_input_hight))
        self._set_camera_preview_size(fs=False)
        self.bind("<Escape>", self._hide_input_window)

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
    # app.attributes("-fullscreen", True)
    # app.focus_force()
    app.bind("<Return>", app._capture)
    app.bind("<Control-s>", app._capture)
    app.bind("<Control-c>", lambda x: app.close_app())
    app.mainloop()
