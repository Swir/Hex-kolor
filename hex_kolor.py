import tkinter as tk
from tkinter import colorchooser

class ColorPaletteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hex Kolor 1.0 by Swir")
        self.root.configure(bg="#F0F0F0")  # Tło programu

        self.current_color = "#000000"  # Domyślny kolor

        self.create_widgets()

    def create_widgets(self):
        self.color_label = self.create_label("Aktualny kolor:", 14, 10)
        self.color_display = self.create_display_label(30, 2)
        self.rgb_label = self.create_label("Składowe RGB:", 14, 10)

        self.red_slider = self.create_slider("Czerwony", "#FF8888")
        self.green_slider = self.create_slider("Zielony", "#88FF88")
        self.blue_slider = self.create_slider("Niebieski", "#8888FF")

        self.update_button = self.create_button("Aktualizuj kolor", self.update_color, "#E0E0E0", 12, 10)
        self.choose_color_button = self.create_button("Wybierz kolor", self.choose_color, "#E0E0E0", 12)
        self.manual_entry_label = self.create_label("Wprowadź kod HEX koloru:", 14, 10)
        self.manual_entry = self.create_entry(12)
        self.manual_update_button = self.create_button("Aktualizuj ręcznie", self.manual_update_color, "#E0E0E0", 12)
        self.copy_button = self.create_button("Kopiuj kod koloru", self.copy_color_code, "#E0E0E0", 12, 10)

    def create_label(self, text, font_size, pady=0):
        label = tk.Label(self.root, text=text, font=("Helvetica", font_size), bg="#F0F0F0")
        label.pack(pady=pady)
        return label

    def create_display_label(self, width, height):
        display_label = tk.Label(self.root, width=width, height=height, relief="solid")
        display_label.pack()
        return display_label

    def create_slider(self, label_text, trough_color):
        slider = tk.Scale(self.root, from_=0, to=255, orient="horizontal", label=label_text,
                          troughcolor=trough_color, sliderlength=20, length=300)
        slider.pack()
        return slider

    def create_button(self, text, command, bg_color, font_size, pady=0):
        button = tk.Button(self.root, text=text, command=command, bg=bg_color, font=("Helvetica", font_size))
        button.pack(pady=pady)
        return button

    def create_entry(self, font_size):
        entry = tk.Entry(self.root, font=("Helvetica", font_size))
        entry.pack()
        return entry

    def update_color(self):
        red = self.red_slider.get()
        green = self.green_slider.get()
        blue = self.blue_slider.get()
        hex_color = f"#{red:02X}{green:02X}{blue:02X}"

        self.color_display.config(bg=hex_color)
        self.color_label.config(text=f"Aktualny kolor: {hex_color}")
        self.current_color = hex_color

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.red_slider.set(int(color[1:3], 16))
            self.green_slider.set(int(color[3:5], 16))
            self.blue_slider.set(int(color[5:], 16))
            self.update_color()

    def manual_update_color(self):
        hex_code = self.manual_entry.get()
        try:
            self.color_display.config(bg=hex_code)
            self.color_label.config(text=f"Aktualny kolor: {hex_code}")
            self.current_color = hex_code
        except:
            pass

    def copy_color_code(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_color)
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorPaletteApp(root)
    root.mainloop()
