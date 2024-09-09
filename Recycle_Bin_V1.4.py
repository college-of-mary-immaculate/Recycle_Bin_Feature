#pip install pywin32 pystray pillow
import ctypes
import tkinter as tk
from tkinter import messagebox
import win32com.client
from PIL import Image, ImageDraw
import pystray
import threading

class RecycleBinManager:
    def __init__(self, bin):
        self.bin = bin
        self.size_entry = None
        self.start_button = None
        self.tray_icon = None
        self.tray_icon_created = False
        self.setup_gui()
        self.create_tray_icon()
    
    def setup_gui(self):
        self.bin.title("Recycle Bin Limiter")
        self.bin.geometry("300x200")
        self.bin.configure(bg="#2E2E2E")
        tk.Label(self.bin, text="Set Recycle Bin Size Limit", font=("Arial", 14, "bold"), fg="#FFFFFF", bg="#2E2E2E").pack(pady=(20, 5))
        tk.Label(self.bin, text="(1-10 GB)", font=("Arial", 10), fg="#CCCCCC", bg="#2E2E2E").pack(pady=(0, 10))
        self.size_entry = tk.Entry(self.bin, justify="center", font=("Arial", 12), width=10, bd=2, relief="solid")
        self.size_entry.pack(pady=(0, 15))
        self.size_entry.insert(0, "")
        self.start_button = tk.Button(self.bin, text="Start Monitoring", font=("Arial", 12, "bold"), command=self.on_start_button_click, bg="#4CAF50", fg="#FFFFFF", padx=10, pady=5, relief="raised")
        self.start_button.pack(pady=20)
        self.start_button.bind("<Enter>", lambda e: self.start_button.config(bg="#45A049"))
        self.start_button.bind("<Leave>", lambda e: self.start_button.config(bg="#4CAF50"))

    def empty_recycle_bin(self):
        SHEmptyRecycleBinW = ctypes.windll.shell32.SHEmptyRecycleBinW
        SHEmptyRecycleBinW(None, None, 1)

    def get_recycle_bin_size(self):
        try:
            shell = win32com.client.Dispatch("Shell.Application")
            recycle_bin = shell.NameSpace(10)
            total_size = 0
            if recycle_bin:
                for item in recycle_bin.Items():
                    total_size += item.Size
                return total_size // (1024 ** 3)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get recycle bin size: {e}")
        return 0

    def set_size_limit(self):
        try:
            size_limit = int(self.size_entry.get())
            if size_limit < 1 or size_limit > 10:
                raise ValueError("Size must be between 1 GB and 10 GB.")
            return size_limit
        except ValueError as e:
            messagebox.showerror("Invalid input", f"{e}")
            return None

    def on_start_button_click(self):
        self.start_button.config(state="disabled")
        self.check_and_empty_bin()

    def check_and_empty_bin(self):
        size_limit = self.set_size_limit()
        if size_limit is None:
            self.start_button.config(state="normal")
            return
        current_size = self.get_recycle_bin_size()
        if current_size >= size_limit:
            self.empty_recycle_bin()
        self.bin.after(1000, self.check_and_empty_bin)
    
    def create_tray_icon(self):
        if not self.tray_icon_created:
            image = Image.new('RGB', (64, 64), (0, 0, 0))
            dc = ImageDraw.Draw(image)
            dc.rectangle((8, 8, 56, 56), fill=(0, 255, 0))

            menu = pystray.Menu(
                pystray.MenuItem("Show", self.show_window),
                pystray.MenuItem("Exit", self.exit_action)
            )
            self.tray_icon = pystray.Icon("recycle_bin_manager", image, menu=menu)
            self.tray_icon_created = True
            threading.Thread(target=self.tray_icon.run).start()

    def show_window(self, icon, item):
        self.bin.deiconify()

    def exit_action(self, icon, item):
        self.bin.destroy()

if __name__ == "__main__":
    bin = tk.Tk()
    app = RecycleBinManager(bin)
    bin.protocol("WM_DELETE_WINDOW", lambda: bin.withdraw())
    bin.mainloop()
    