import pyautogui as pag
import threading
import time
import tkinter as tk
import keyboard
import json
import os

CONFIG_FILE = "keybinds.json"

locations = [
    (946, 253),
    (562, 397),
    (427, 617),
    (596, 859),
    (945, 918),
    (1358, 832),
    (1458, 625),
    (1355, 371),
]

pause_event = threading.Event()
running_event = threading.Event()

default_hotkeys = {
    "pause": "shift+p",
    "resume": "shift+u"
}

hotkeys = {}
hotkey_handles = []


# ---------------- SAVE SYSTEM ----------------

def load_hotkeys():
    global hotkeys
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                hotkeys = json.load(f)
        except:
            hotkeys = default_hotkeys.copy()
    else:
        hotkeys = default_hotkeys.copy()


def save_hotkeys():
    with open(CONFIG_FILE, "w") as f:
        json.dump(hotkeys, f, indent=4)


def rebind_hotkeys():
    global hotkey_handles

    for h in hotkey_handles:
        try:
            keyboard.remove_hotkey(h)
        except:
            pass

    hotkey_handles.clear()

    hotkey_handles.append(keyboard.add_hotkey(hotkeys["pause"], pause_program))
    hotkey_handles.append(keyboard.add_hotkey(hotkeys["resume"], resume_program))


# ---------------- CONTROLS ----------------

def pause_program():
    pause_event.set()


def resume_program():
    pause_event.clear()


def start_program():
    running_event.set()


# ---------------- LOOP ----------------

def smart_sleep(seconds):
    end = time.time() + seconds
    while time.time() < end:
        while pause_event.is_set():
            time.sleep(0.01)
        time.sleep(0.01)


def runner():
    while True:

        if not running_event.is_set():
            time.sleep(0.1)
            continue

        for i, (x, y) in enumerate(locations):

            while pause_event.is_set():
                time.sleep(0.01)

            pag.click(x, y)

            if i in (1, 3, 5, 7):
                smart_sleep(1)

        smart_sleep(0.05)


# ---------------- KEY CAPTURE ----------------

def capture_hotkey(action, label):
    label.config(text="Press keys...")

    def on_event(e):
        if e.event_type != "down":
            return

        key = e.name

        if key in ["shift", "ctrl", "alt"]:
            return

        combo = []

        if keyboard.is_pressed("shift"):
            combo.append("shift")
        if keyboard.is_pressed("ctrl"):
            combo.append("ctrl")
        if keyboard.is_pressed("alt"):
            combo.append("alt")

        combo.append(key)

        hotkeys[action] = "+".join(combo)

        label.config(text=hotkeys[action])

        keyboard.unhook_all()

    keyboard.hook(on_event)


# ---------------- STYLE ----------------

def dark_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg="#1a1a1a",
        fg="white",
        activebackground="#2a2a2a",
        activeforeground="white",
        relief="flat",
        bd=0,
        highlightthickness=0
    )


# ---------------- INIT ----------------

load_hotkeys()
rebind_hotkeys()

threading.Thread(target=runner, daemon=True).start()


# ---------------- UI ----------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Automation Controller")
        self.geometry("380x420")
        self.configure(bg="#0f0f12")
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self.build_ui()
        self.refresh_state()

    def build_ui(self):

        tk.Label(
            self,
            text="Dumb Fish Game Auto Clicker",
            fg="white",
            bg="#0f0f12",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        self.state_label = tk.Label(
            self,
            text="Status: OFF",
            fg="gray",
            bg="#0f0f12"
        )
        self.state_label.pack()

        dark_button(self, "Start", start_program).pack(fill="x", pady=2)
        dark_button(self, "Pause", pause_program).pack(fill="x", pady=2)
        dark_button(self, "Resume", resume_program).pack(fill="x", pady=2)

        tk.Label(
            self,
            text="KEYBINDS (click then press keys)",
            fg="white",
            bg="#0f0f12"
        ).pack(pady=10)

        self.pause_label = tk.Label(self, text=hotkeys["pause"], fg="cyan", bg="#0f0f12")
        self.pause_label.pack()

        self.resume_label = tk.Label(self, text=hotkeys["resume"], fg="cyan", bg="#0f0f12")
        self.resume_label.pack()

        dark_button(
            self,
            "Set PAUSE Key",
            lambda: capture_hotkey("pause", self.pause_label)
        ).pack(fill="x", pady=2)

        dark_button(
            self,
            "Set RESUME Key",
            lambda: capture_hotkey("resume", self.resume_label)
        ).pack(fill="x", pady=2)

        dark_button(self, "Save Keybinds", self.save).pack(fill="x", pady=10)
        dark_button(self, "Reset Defaults", self.reset).pack(fill="x", pady=2)

    def save(self):
        save_hotkeys()
        rebind_hotkeys()

    def reset(self):
        global hotkeys

        hotkeys = default_hotkeys.copy()

        self.pause_label.config(text=hotkeys["pause"])
        self.resume_label.config(text=hotkeys["resume"])

        save_hotkeys()
        rebind_hotkeys()

    def refresh_state(self):

        if pause_event.is_set():
            self.state_label.config(text="Status: PAUSED", fg="orange")
        elif running_event.is_set():
            self.state_label.config(text="Status: RUNNING", fg="green")
        else:
            self.state_label.config(text="Status: OFF", fg="gray")

        self.after(150, self.refresh_state)


App().mainloop()