import tkinter as tk
from tkinter import filedialog, colorchooser
import os, subprocess, json, time, ctypes
import winsound

# --- THE PATH SNIPER (v1.3.3 - Corrected Folder Name) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Changed "sound" to "sounds" to match your PC!
ASSET_PATH = os.path.join(BASE_DIR, "assets", "sounds", "click.wav")

DATA_FILE = os.path.join(BASE_DIR, "altdesk_v1_3_3.json")
GRID_SIZE = 20

print(f"--- Path Sniper Diagnostic ---")
print(f"Looking for: {ASSET_PATH}")
if os.path.exists(ASSET_PATH):
    print("✅ SUCCESS: The 'sounds' folder is connected!")
else:
    print("❌ ERROR: Still missing. Is the file definitely named 'click.wav'?")
print(f"------------------------------")
class DesktopIcon(tk.Frame):
    def __init__(self, parent, app, path, x, y):
        super().__init__(parent, bg="#1a1a1a")
        self.app = app
        self.path = path
        self.name = os.path.basename(path)
        
        self.img = tk.Label(self, text="📄", font=("Arial", 26), bg="#1a1a1a", fg="white")
        self.img.pack()
        self.lbl = tk.Label(self, text=self.name, font=("Segoe UI", 9), bg="#1a1a1a", fg="white", wraplength=80)
        self.lbl.pack()
        self.place(x=x, y=y)
        
        for w in (self, self.img, self.lbl):
            w.bind("<Button-1>", self.on_click)
            w.bind("<B1-Motion>", self.on_drag)
            w.bind("<ButtonRelease-1>", self.on_release)
            w.bind("<Double-Button-1>", lambda e: self.open_file())

    def on_click(self, event):
        self.app.play_click() # CLICK: When picking up an icon
        self._drag_start_x, self._drag_start_y = event.x, event.y
        self.lift()

    def on_drag(self, event):
        nx = self.winfo_x() + (event.x - self._drag_start_x)
        ny = self.winfo_y() + (event.y - self._drag_start_y)
        self.place(x=nx, y=ny)

    def on_release(self, event):
        self.app.play_click() # CLICK: When dropping an icon
        sx, sy = (self.winfo_x()//GRID_SIZE)*GRID_SIZE, (self.winfo_y()//GRID_SIZE)*GRID_SIZE
        self.place(x=sx, y=sy)
        self.app.save_data()

    def open_file(self):
        self.app.play_click() # CLICK: When double clicking to open
        try: os.startfile(self.path) if os.name == 'nt' else subprocess.Popen(['open', self.path])
        except: pass

class AltDesk:
    def __init__(self, root):
        self.root = root
        self.root.title("AltDesk v1.3.3 (Tactile Update)")
        self.root.geometry("1100x750")
        self.root.configure(bg="#1a1a1a")
        
        self.root.bind("<F11>", lambda e: [self.play_click(), self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))])
        self.root.bind("<Escape>", lambda e: [self.play_click(), self.root.attributes("-fullscreen", False)])
        
        self.draw_mode = False
        self.erase_mode = False
        self.paint_color = "white" 
        self.icons = []
        self.lines_data = []

        self.canvas = tk.Canvas(root, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.paint_or_erase)

        # --- TASKBAR ---
        self.taskbar = tk.Frame(root, bg="#0a0a0a", height=50)
        self.taskbar.pack(side="bottom", fill="x")
        
        self.color_prev = tk.Frame(self.taskbar, bg=self.paint_color, width=15, height=15)
        self.color_prev.pack(side="left", padx=5)
        
        # All buttons now have play_click() inside their command lambda
        tk.Button(self.taskbar, text="🎨", bg="#333", fg="white", command=lambda:[self.play_click(), self.choose_color()], relief="flat").pack(side="left", padx=2)
        tk.Button(self.taskbar, text="❖ Add", bg="#333", fg="white", command=lambda:[self.play_click(), self.add_file()], relief="flat").pack(side="left", padx=5)
        
        self.draw_btn = tk.Button(self.taskbar, text="🖊 Draw: OFF", bg="#333", fg="white", command=lambda:[self.play_click(), self.toggle_draw()], relief="flat")
        self.draw_btn.pack(side="left", padx=5)
        
        self.erase_btn = tk.Button(self.taskbar, text="🧽 Erase: OFF", bg="#333", fg="white", command=lambda:[self.play_click(), self.toggle_erase()], relief="flat")
        self.erase_btn.pack(side="left", padx=5)
        
        tk.Button(self.taskbar, text="🧹 Clear Ink", bg="#442222", fg="white", command=lambda:[self.play_click(), self.clear_ink()], relief="flat").pack(side="left", padx=5)

        self.bat_lbl = tk.Label(self.taskbar, text="🔋 --%", bg="#0a0a0a", fg="#aaa", font=("Consolas", 10))
        self.bat_lbl.pack(side="right", padx=10)
        
        self.update_sys()
        self.load_data()

    def play_click(self):
        """Global sound trigger"""
        if os.path.exists(ASSET_PATH):
            try:
                # SND_ASYNC lets the sound play without freezing the app
                winsound.PlaySound(ASSET_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"Audio Error: {e}")

    def toggle_draw(self):
        self.draw_mode, self.erase_mode = not self.draw_mode, False
        self.update_buttons()

    def toggle_erase(self):
        self.erase_mode, self.draw_mode = not self.erase_mode, False
        self.update_buttons()

    def update_buttons(self):
        self.draw_btn.config(text=f"🖊 Draw: {'ON' if self.draw_mode else 'OFF'}", fg=self.paint_color if self.draw_mode else "white")
        self.erase_btn.config(text=f"🧽 Erase: {'ON' if self.erase_mode else 'OFF'}", fg="pink" if self.erase_mode else "white")
        self.canvas.config(cursor="pencil" if self.draw_mode else "dot" if self.erase_mode else "arrow")

    def choose_color(self):
        color = colorchooser.askcolor(title="Select Paint Color")[1]
        if color:
            self.paint_color = color
            self.color_prev.config(bg=color)
            if self.draw_mode: self.draw_btn.config(fg=color)

    def start_draw(self, event): 
        # Click when you start to draw or erase on the canvas
        if self.draw_mode or self.erase_mode:
            self.play_click()
        self.lx, self.ly = event.x, event.y

    def paint_or_erase(self, event):
        if self.draw_mode:
            self.canvas.create_line(self.lx, self.ly, event.x, event.y, fill=self.paint_color, width=2, tags="ink")
            self.lines_data.append({"coords": [self.lx, self.ly, event.x, event.y], "color": self.paint_color})
            self.lx, self.ly = event.x, event.y
        elif self.erase_mode:
            target = self.canvas.find_closest(event.x, event.y)
            if "ink" in self.canvas.gettags(target):
                self.canvas.delete(target)

    def clear_ink(self):
        self.canvas.delete("ink")
        self.lines_data = []
        self.save_data()

    def update_sys(self):
        if os.name == 'nt':
            try:
                class PS(ctypes.Structure): _fields_ = [('A', ctypes.c_byte), ('B', ctypes.c_byte), ('P', ctypes.c_byte)]
                s = PS(); ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s))
                self.bat_lbl.config(text=f"🔋 {s.P}%")
            except: pass
        self.root.after(5000, self.update_sys)

    def add_file(self):
        p = filedialog.askopenfilename()
        if p: self.icons.append(DesktopIcon(self.canvas, self, p, 50, 50)); self.save_data()

    def save_data(self):
        pay = {"icons": [{"path": i.path, "x": i.winfo_x(), "y": i.winfo_y()} for i in self.icons],
               "drawings": self.lines_data}
        with open(DATA_FILE, "w") as f: json.dump(pay, f)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    d = json.load(f)
                    for l in d.get("drawings", []): self.canvas.create_line(l["coords"], fill=l.get("color", "white"), width=2, tags="ink")
                    for i in d.get("icons", []): self.icons.append(DesktopIcon(self.canvas, self, i["path"], i["x"], i["y"]))
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = AltDesk(root)
    print(f"--- Audio Diagnostic ---")
    print(f"Looking for: {ASSET_PATH}")
    print(f"Status: {'FOUND' if os.path.exists(ASSET_PATH) else 'NOT FOUND'}")
    root.mainloop()
