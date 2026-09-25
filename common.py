import json

from pynput import keyboard

RECORDING_FILE = "recording.json"
MIN_REPEAT = -1               # -1 = play in reverse
MAX_REPEAT = 999
MOVE_INTERVAL = 0.01          # save mouse move events every 10ms, otherwise the file gets huge


def key_name(key):
    """pynput key object -> plain string"""
    if isinstance(key, keyboard.KeyCode) and key.char is not None:
        return key.char
    return str(key).replace("Key.", "")


def key_object(name):
    """plain string -> pynput key object"""
    if len(name) == 1:
        return name
    return getattr(keyboard.Key, name, name)


def save_events(events):
    with open(RECORDING_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=1)


def load_events():
    with open(RECORDING_FILE, encoding="utf-8") as f:
        return json.load(f)


def reverse_events(events):
    """Mirror the timeline. press/release is flipped so nothing stays held."""
    total = events[-1]["time"]
    out = []
    for e in reversed(events):
        e = dict(e)
        e["time"] = round(total - e["time"], 4)
        if "pressed" in e:
            e["pressed"] = not e["pressed"]
        out.append(e)
    return out