import json
import tkinter as tk

from pynput import keyboard, mouse

from common import MAX_REPEAT, MIN_REPEAT, RECORDING_FILE, load_events
from player import Player
from recorder import Recorder

INFO = (
    "Press ESC to quit\n"
    "Please don't use your mouse when Player is playing\n"
    "\n"
    "Maximum repeat is 999 and if you want it to\n"
    "play it in reverse write -1 in Repeat"
)


class App:
    def __init__(self, root):
        self.root = root
        root.title("Macro")
        root.resizable(False, False)

        self.recorder = Recorder()
        self.player = Player(self._player_finished)

        self._build_ui()
        self._start_listeners()
        root.protocol("WM_DELETE_WINDOW", self.quit)

    # -- ui ---------------------------------------------------------------
    def _build_ui(self):
        root = self.root
        root.columnconfigure(0, weight=1)

        tk.Label(root, text=INFO, justify="left").grid(
            row=0, column=0, sticky="nw", padx=16, pady=(14, 0)
        )

        repeat_box = tk.Frame(root)
        repeat_box.grid(row=0, column=1, sticky="ne", padx=16, pady=(14, 0))

        tk.Label(repeat_box, text="Repeat:").grid(row=0, column=0, padx=(0, 6))

        vcmd = (root.register(self._validate_repeat), "%P")
        self.repeat_var = tk.StringVar(value="1")
        tk.Entry(
            repeat_box, textvariable=self.repeat_var, width=6,
            justify="right", validate="key", validatecommand=vcmd,
        ).grid(row=0, column=1)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status_var, fg="#555").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(18, 0)
        )

        buttons = tk.Frame(root)
        buttons.grid(row=2, column=0, columnspan=2, pady=(24, 18))

        tk.Button(
            buttons, text="Start/Stop\nRecording (F6)", width=20, height=3,
            command=self.toggle_recording,
        ).grid(row=0, column=0, padx=18)

        tk.Button(
            buttons, text="Start/Stop Player\n(F7)", width=20, height=3,
            command=self.toggle_player,
        ).grid(row=0, column=1, padx=18)

    @staticmethod
    def _validate_repeat(value):
        if value in ("", "-"):
            return True
        try:
            n = int(value)
        except ValueError:
            return False
        return MIN_REPEAT <= n <= MAX_REPEAT

    def set_status(self, text):
        self.status_var.set(text)

    # -- global hotkeys ---------------------------------------------------
    def _start_listeners(self):
        self.mouse_listener = mouse.Listener(
            on_move=self.recorder.on_move,
            on_click=self.recorder.on_click,
            on_scroll=self.recorder.on_scroll,
        )
        self.kb_listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self.mouse_listener.start()
        self.kb_listener.start()

    def _on_press(self, key):
        # kontrol tuslari kayda girmez
        if key == keyboard.Key.f6:
            self.root.after(0, self.toggle_recording)
        elif key == keyboard.Key.f7:
            self.root.after(0, self.toggle_player)
        elif key == keyboard.Key.esc:
            self.root.after(0, self.quit)
        else:
            self.recorder.on_press(key)

    def _on_release(self, key):
        if key in (keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.esc):
            return
        self.recorder.on_release(key)

    # -- actions ----------------------------------------------------------
    def toggle_recording(self):
        if self.player.playing:
            self.set_status("Player is running")
            return
        if self.recorder.recording:
            count = self.recorder.stop()
            self.set_status(f"Saved {count} events to {RECORDING_FILE}")
        else:
            self.recorder.start()
            self.set_status("Recording...")

    def toggle_player(self):
        if self.recorder.recording:
            self.set_status("Recorder is running")
            return
        if self.player.playing:
            self.player.stop()
            self.set_status("Stopping...")
            return

        try:
            repeat = int(self.repeat_var.get())
        except ValueError:
            self.set_status("Repeat must be a whole number")
            return
        if not MIN_REPEAT <= repeat <= MAX_REPEAT:
            self.set_status(f"Repeat must be between {MIN_REPEAT} and {MAX_REPEAT}")
            return

        try:
            events = load_events()
        except FileNotFoundError:
            self.set_status(f"{RECORDING_FILE} not found - record something first")
            return
        except json.JSONDecodeError:
            self.set_status(f"{RECORDING_FILE} is not valid JSON")
            return
        if not events:
            self.set_status("Recording is empty")
            return

        self.player.start(events, repeat)
        self.set_status("Playing - reverse" if repeat == MIN_REPEAT else "Playing...")

    def _player_finished(self):
        # player thread'inden gelir, ui'ye ana thread'den dokun
        self.root.after(0, lambda: self.set_status("Ready"))

    # -- quit -------------------------------------------------------------
    def quit(self):
        self.player.stop()
        if self.recorder.recording:
            self.recorder.stop()
        self.mouse_listener.stop()
        self.kb_listener.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()