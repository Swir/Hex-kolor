"""Shared Polish/English HEX color utility."""
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
import tkinter as tk
from tkinter import colorchooser, ttk

VERSION = "1.11.0"
TEXT = {
    "pl": {"title": "Hex Kolor", "current": "Aktualny kolor", "red": "Czerwony", "green": "Zielony", "blue": "Niebieski", "manual": "Kod HEX (#RRGGBB lub #RGB):", "apply": "Zastosuj HEX", "choose": "Wybierz kolor…", "copy": "Kopiuj kod", "copied": "Skopiowano", "invalid": "Wpisz 3 lub 6 znaków HEX (0–9, A–F), z # lub bez.", "clipboard": "Nie można teraz skopiować kodu. Spróbuj ponownie."},
    "en": {"title": "HEX Color", "current": "Current color", "red": "Red", "green": "Green", "blue": "Blue", "manual": "HEX code (#RRGGBB or #RGB):", "apply": "Apply HEX", "choose": "Choose color…", "copy": "Copy code", "copied": "Copied", "invalid": "Enter 3 or 6 HEX digits (0–9, A–F), with or without #.", "clipboard": "Cannot copy the code right now. Please try again."},
}


@dataclass(frozen=True)
class Color:
    red: int
    green: int
    blue: int

    def __post_init__(self):
        for name in ("red", "green", "blue"):
            object.__setattr__(self, name, min(max(int(getattr(self, name)), 0), 255))

    def to_hex(self):
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"

    @classmethod
    def from_hex(cls, text):
        value = text.strip()
        if not re.fullmatch(r"#?(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value):
            raise ValueError("Invalid HEX color")
        value = value.removeprefix("#")
        if len(value) == 3:
            value = "".join(char * 2 for char in value)
        return cls(*(int(value[index:index + 2], 16) for index in (0, 2, 4)))


class ColorPaletteApp:
    def __init__(self, root, language="pl"):
        self.root = root
        self.text = TEXT[language]
        self.current_color = Color(0, 0, 0)
        self._syncing = False
        root.title(f"{self.text['title']} {VERSION} — Swir")
        root.minsize(360, 480)
        root.columnconfigure(0, weight=1)
        frame = ttk.Frame(root, padding=18)
        frame.grid(sticky="nsew")
        frame.columnconfigure(0, weight=1)
        self.label = tk.StringVar(root)
        self.manual = tk.StringVar(root)
        self.status = tk.StringVar(root)
        ttk.Label(frame, textvariable=self.label, font=("Segoe UI", 13)).grid(row=0, sticky="w", pady=(0, 10))
        self.preview = tk.Label(frame, height=3, relief="solid", borderwidth=1)
        self.preview.grid(row=1, sticky="ew", pady=(0, 10))
        self.sliders = []
        for row, key in enumerate(("red", "green", "blue"), start=2):
            slider = tk.Scale(frame, from_=0, to=255, orient="horizontal", label=self.text[key], length=300,
                              command=lambda _value: self.update_color(), highlightthickness=0)
            slider.grid(row=row, sticky="ew")
            self.sliders.append(slider)
        self.red_slider, self.green_slider, self.blue_slider = self.sliders
        ttk.Label(frame, text=self.text["manual"]).grid(row=5, sticky="w", pady=(10, 3))
        self.manual_entry = ttk.Entry(frame, textvariable=self.manual)
        self.manual_entry.grid(row=6, sticky="ew")
        self.manual_entry.bind("<Return>", lambda _event: self.manual_update_color())
        self.apply_button = ttk.Button(frame, text=self.text["apply"], command=self.manual_update_color)
        self.apply_button.grid(row=7, sticky="ew", pady=5)
        ttk.Button(frame, text=self.text["choose"], command=self.choose_color).grid(row=8, sticky="ew", pady=3)
        ttk.Button(frame, text=self.text["copy"], command=self.copy_color_code).grid(row=9, sticky="ew", pady=3)
        ttk.Label(frame, textvariable=self.status, wraplength=330).grid(row=10, sticky="ew", pady=(8, 0))
        self.set_color(self.current_color)

    def set_color(self, color):
        self._syncing = True
        try:
            for slider, value in zip(self.sliders, (color.red, color.green, color.blue)):
                slider.set(value)
            self.current_color = color
            value = color.to_hex()
            self.preview.configure(bg=value)
            self.label.set(f"{self.text['current']}: {value}")
            self.manual.set(value)
            self.status.set("")
        finally:
            self._syncing = False

    def update_color(self):
        if not self._syncing:
            self.set_color(Color(*(slider.get() for slider in self.sliders)))

    def is_valid_hex(self, text):
        try:
            Color.from_hex(text)
            return True
        except ValueError:
            return False

    def manual_update_color(self):
        try:
            color = Color.from_hex(self.manual.get())
        except ValueError:
            self.status.set(self.text["invalid"])
            return False
        self.set_color(color)
        return True

    def choose_color(self):
        selected = colorchooser.askcolor(color=self.current_color.to_hex(), parent=self.root)[1]
        if selected:
            self.set_color(Color.from_hex(selected))

    def copy_color_code(self):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_color.to_hex())
            self.status.set(f"{self.text['copied']}: {self.current_color.to_hex()}")
        except tk.TclError:
            self.status.set(self.text["clipboard"])


def self_test(report, language):
    root = None
    result = {"application": "Hex-Color", "language": language, "version": VERSION, "passed": False}
    try:
        root = tk.Tk()
        root.withdraw()
        app = ColorPaletteApp(root, language)
        root.update_idletasks()
        assert app.preview.cget("background") == "#000000"
        app.manual.set(" #a3f ")
        app.apply_button.invoke()
        root.update_idletasks()
        assert app.current_color.to_hex() == "#AA33FF"
        assert [slider.get() for slider in app.sliders] == [170, 51, 255]
        app.manual.set("#²²0000")
        assert not app.manual_update_color() and app.status.get()
        assert app.current_color.to_hex() == "#AA33FF"
        app.red_slider.set(0)
        app.update_color()
        assert app.current_color.to_hex() == "#0033FF"
        result.update(passed=True, checks=["Tk widgets", "manual HEX button", "RGB synchronization", "invalid input", "slider update"])
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
    finally:
        if root is not None:
            root.destroy()
        Path(report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if result["passed"] else 1


def main(language="pl"):
    if len(sys.argv) == 3 and sys.argv[1] == "--self-test":
        return self_test(sys.argv[2], language)
    root = tk.Tk()
    ColorPaletteApp(root, language)
    root.mainloop()
    return 0
