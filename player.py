import threading
import time

from pynput import keyboard, mouse

from common import MIN_REPEAT, key_object, reverse_events


class Player:
    def __init__(self, on_finish):
        self.on_finish = on_finish
        self.stop_event = threading.Event()
        self.thread = None
        self.mouse = mouse.Controller()
        self.keyboard = keyboard.Controller()

    @property
    def playing(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, events, repeat):
        self.stop_event.clear()
        self.thread = threading.Thread(
            target=self._run, args=(events, repeat), daemon=True
        )
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def _run(self, events, repeat):
        if repeat == MIN_REPEAT:          # -1 -> play backwards, once
            events = reverse_events(events)
            passes = 1
        else:
            passes = repeat

        for _ in range(passes):
            if self.stop_event.is_set():
                break
            start = time.perf_counter()
            for e in events:
                if self.stop_event.is_set():
                    break
                # her olayi BASLANGICA gore hesapla, gecikme birikmesin
                delay = start + e["time"] - time.perf_counter()
                if delay > 0:
                    time.sleep(delay)
                self._dispatch(e)

        self.on_finish()

    def _dispatch(self, e):
        kind = e["type"]
        if kind == "move":
            self.mouse.position = (e["x"], e["y"])
        elif kind == "click":
            self.mouse.position = (e["x"], e["y"])
            button = mouse.Button[e["button"]]
            if e["pressed"]:
                self.mouse.press(button)
            else:
                self.mouse.release(button)
        elif kind == "scroll":
            self.mouse.position = (e["x"], e["y"])
            self.mouse.scroll(e["dx"], e["dy"])
        elif kind == "key":
            key = key_object(e["key"])
            if e["pressed"]:
                self.keyboard.press(key)
            else:
                self.keyboard.release(key)