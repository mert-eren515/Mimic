import time

from common import MOVE_INTERVAL, key_name, save_events


class Recorder:
    def __init__(self):
        self.events = []
        self.recording = False
        self.t0 = 0.0
        self.last_move = 0.0

    def start(self):
        self.events = []
        self.t0 = time.perf_counter()
        self.last_move = 0.0
        self.recording = True

    def stop(self):
        self.recording = False
        save_events(self.events)
        return len(self.events)

    def add(self, **event):
        if not self.recording:
            return
        t = round(time.perf_counter() - self.t0, 4)
        self.events.append({"time": t, **event})

    def on_move(self, x, y):
        if not self.recording:
            return
        now = time.perf_counter()
        if now - self.last_move < MOVE_INTERVAL:
            return
        self.last_move = now
        self.add(type="move", x=x, y=y)

    def on_click(self, x, y, button, pressed):
        self.add(type="click", x=x, y=y, button=button.name, pressed=pressed)

    def on_scroll(self, x, y, dx, dy):
        self.add(type="scroll", x=x, y=y, dx=dx, dy=dy)

    def on_press(self, key):
        self.add(type="key", key=key_name(key), pressed=True)

    def on_release(self, key):
        self.add(type="key", key=key_name(key), pressed=False)