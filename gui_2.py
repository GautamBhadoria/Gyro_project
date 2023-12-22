import tkinter as tk
from tkinter import filedialog, ttk
import cv2
from PIL import Image, ImageTk

class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg='dark grey')  # Set background color of the root window

        # Video Player Variables
        self.video_path = ""
        self.cap = None
        self.fps = 30
        self.is_fullscreen = True
        self.vr_mode = False
        self.total_frames = 0
        self.paused = False
        self.after_id = None

        # VR Mode Variables
        self.vr_mode = False

        # GUI Components
        self.video_dropdown = None
        self.fps_scale = None
        self.play_button = None
        self.vr_button = None
        self.browse_button = None
        self.canvas = None
        self.create_widgets()

    def create_widgets(self):
        # Frame for Buttons
        top_frame = tk.Frame(self.root, bg='dark grey')  # Set frame background
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Browse Button
        self.browse_button = tk.Button(top_frame, text="Browse", command=self.browse_video, bg='grey')
        self.browse_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Play Button
        self.play_button = tk.Button(top_frame, text="Play", command=self.play_video, bg='grey')
        self.play_button.pack(side=tk.LEFT, padx=10, pady=10)

        # VR Mode Button
        self.vr_button = tk.Button(top_frame, text="VR Mode", command=self.toggle_vr_mode, bg='grey')
        self.vr_button.pack(side=tk.LEFT, padx=10, pady=10)

        # FPS Scale
        self.fps_scale = tk.Scale(top_frame, from_=0, to=60, orient=tk.HORIZONTAL, command=self.adjust_fps, bg='grey')
        self.fps_scale.set(self.fps)
        self.fps_scale.pack(side=tk.LEFT, padx=10, pady=10)

        # Fullscreen Button
        self.fullscreen_button = tk.Button(top_frame, text="Fullscreen", command=self.toggle_fullscreen, bg='grey')
        self.fullscreen_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Canvas for Video Display
        self.canvas = tk.Canvas(self.root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill=tk.X, side=tk.BOTTOM)

    def browse_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])

    def adjust_fps(self, val):
        self.fps = max(0, int(val))  # Prevent division by zero
        if self.cap and self.cap.isOpened():
            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.update_video()  # Start update loop with new FPS

    def play_video(self):
        if self.cap:
            self.cap.release()
        
        self.fps = self.fps_scale.get()
        self.cap = cv2.VideoCapture(self.video_path)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        if not self.cap.isOpened():
            print("Error: Unable to open video.")
            return
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.progress["maximum"] = self.total_frames
        self.update_video()

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            if self.vr_mode:
                self.display_vr_frame(frame)
            else:
                self.display_frame(frame)
            if self.fps==0:
                self.root.after(int(10000000), self.update_video)
            else:
                self.root.after(int(1000 / self.fps), self.update_video)
            self.update_progress_bar()
        else:
            self.cap.release()
    def display_frame(self, frame):
        # Resize frame to full canvas size
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        frame = cv2.resize(frame, (width, height))
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.img = img  # Keep a reference.

    def update_progress_bar(self):
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.progress["value"] = current_frame
    def display_vr_frame(self, frame):
        # Resize the frame to half width for side-by-side VR
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        frame = cv2.resize(frame, (width // 2, height))
        
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)

        # Display the same video side by side
        self.canvas.config(width=img.width() * 2, height=img.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.create_image(img.width(), 0, anchor=tk.NW, image=img)
        self.canvas.img = img

    def toggle_vr_mode(self):
        self.vr_mode = not self.vr_mode
        if self.vr_mode:
            self.play_button.config(state=tk.DISABLED)
            self.vr_button.config(text="Exit VR Mode")
        else:
            self.play_button.config(state=tk.NORMAL)
            self.vr_button.config(text="VR Mode")

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def on_close(self):
        if self.cap:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
