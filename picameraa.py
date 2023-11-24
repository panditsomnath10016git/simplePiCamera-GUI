# for testing without physical camera
class PiCamera:
    def __init__(self,**kwargs):
        self.preview_fullscreen = True
        self.preview_window = 0
        self.annotate_background = 0
        self.annotate_text_size = 0
        self.annotate_text = ''
        pass
    def start_preview(self,**kwargs):
        pass
    def stop_preview(self,**kwargs):
        pass
    def capture(self,**kwargs):
        pass
    def close(self,**kwargs):
        pass

    pass