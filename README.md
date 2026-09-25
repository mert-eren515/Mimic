# Mimic

A simple mouse and keyboard macro recorder built with Python, Tkinter and `pynput`.

## Download

Download `Mimic.exe` from the [Releases](../../releases/latest) and run it. No Python needed (Windows only).

Windows may show a SmartScreen warning because the app isn't signed. Click **More info → Run anyway**.

## Run from source

### Requirements

- Python 3
- pynput

```bash
pip install pynput
```

## Usage

```bash
python main.py
```

| Key | Action |
| --- | --- |
| F6  | Start/stop recording |
| F7  | Start/stop playback |
| ESC | Quit |

- Recordings are saved to `recording.json`.
- **Repeat** sets how many times the recording plays (1–999).
- Set **Repeat** to `-1` to play the recording once in reverse.
- Don't use your mouse while playback is running.
