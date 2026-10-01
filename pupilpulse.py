# ==============================================================================
# FILE: mobile_pupil_app.py (Python GUI App with USB & ESP32-CAM Support)
# ==============================================================================

import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image
import time
import csv

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MobilePupilApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pupil Metrics Studio")
        self.geometry("420x780")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Tracking State Variables
        self.camera_source = 0  # Default: local webcam
        self.cap = cv2.VideoCapture(self.camera_source)
        self.is_tracking = True
        self.history_len = 100
        self.radius_history = [0] * self.history_len
        self.logged_data = []

        # Top App Bar
        self.header_frame = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#1a1a1a")
        self.header_frame.pack(fill="x", side="top")

        self.app_title = ctk.CTkLabel(
            self.header_frame, 
            text="👁️ Pupil Metrics Studio", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.app_title.pack(pady=12)

        # Page Container
        self.page_container = ctk.CTkFrame(self, fg_color="transparent")
        self.page_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Pages
        self.pages = {}
        self.pages["home"] = self.create_home_page()
        self.pages["tracker"] = self.create_tracker_page()
        self.pages["guide"] = self.create_guide_page()
        self.pages["about"] = self.create_about_page()

        # Bottom Navigation Bar
        self.navbar = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#1a1a1a")
        self.navbar.pack(fill="x", side="bottom")

        self.nav_buttons = {}
        nav_items = [
            ("home", "🏠 Home"),
            ("tracker", "👁️ Tracker"),
            ("guide", "📊 Guide"),
            ("about", "ℹ About")
        ]

        for page_id, label in nav_items:
            btn = ctk.CTkButton(
                self.navbar,
                text=label,
                width=85,
                height=40,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#2b2b2b",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda p=page_id: self.show_page(p)
            )
            btn.pack(side="left", expand=True, padx=2, pady=10)
            self.nav_buttons[page_id] = btn

        self.current_page = None
        self.show_page("home")
        self.update_frame()

    def show_page(self, page_name):
        for name, frame in self.pages.items():
            frame.pack_forget()
            self.nav_buttons[name].configure(fg_color="transparent", text_color="#dce4ee")

        self.pages[page_name].pack(fill="both", expand=True)
        self.nav_buttons[page_name].configure(fg_color="#1f538d", text_color="white")
        self.current_page = page_name

    def create_home_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")

        welcome_card = ctk.CTkFrame(frame, corner_radius=15)
        welcome_card.pack(fill="x", pady=10)

        ctk.CTkLabel(welcome_card, text="Welcome to Pupil Tracker", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(welcome_card, text="Real-time ocular analysis supporting USB Webcams and ESP32-CAM streams over Wi-Fi.", wraplength=350, justify="left", text_color="#aaaaaa").pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkButton(
            frame, 
            text="▶️ Launch Pupil Tracker", 
            height=45, 
            corner_radius=22,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda: self.show_page("tracker")
        ).pack(fill="x", pady=10)

        features_card = ctk.CTkFrame(frame, corner_radius=15)
        features_card.pack(fill="x", pady=10)

        ctk.CTkLabel(features_card, text="Hardware Compatibility", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))
        features = [
            "📷 USB 2.0/3.0 Webcam Support (Index 0)",
            "📡 ESP32-CAM Wi-Fi MJPEG Stream Support",
            "⚡ Real-Time Thresholding & Contour Extraction",
            "💾 CSV Session Exporting"
        ]
        for f in features:
            ctk.CTkLabel(features_card, text=f, text_color="#cccccc").pack(anchor="w", padx=20, pady=3)

        ctk.CTkLabel(features_card, text="").pack(pady=5)
        return frame

    def create_tracker_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")

        # Camera Stream Connection Box
        source_card = ctk.CTkFrame(frame, corner_radius=12)
        source_card.pack(fill="x", pady=(5, 5))

        ctk.CTkLabel(source_card, text="Source (0 for Webcam or ESP32 URL):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=10, pady=(6, 2))
        
        self.source_entry = ctk.CTkEntry(source_card, placeholder_text="http://192.168.1.50/stream", height=30)
        self.source_entry.insert(0, "0")
        self.source_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=(0, 8))

        connect_btn = ctk.CTkButton(source_card, text="Connect", width=70, height=30, command=self.change_camera_source)
        connect_btn.pack(side="right", padx=(5, 10), pady=(0, 8))

        # Video Label
        cam_card = ctk.CTkFrame(frame, corner_radius=12)
        cam_card.pack(fill="x", pady=5)
        self.video_label = ctk.CTkLabel(cam_card, text="Connecting Camera...")
        self.video_label.pack(padx=5, pady=5)

        # Graph Label
        graph_card = ctk.CTkFrame(frame, corner_radius=12)
        graph_card.pack(fill="x", pady=5)
        self.graph_label = ctk.CTkLabel(graph_card, text="Rendering Graph...")
        self.graph_label.pack(padx=5, pady=5)

        # Analytics Bar
        stats_card = ctk.CTkFrame(frame, corner_radius=12)
        stats_card.pack(fill="x", pady=5)

        self.stats_min_label = ctk.CTkLabel(stats_card, text="Min: -- px", font=ctk.CTkFont(size=12))
        self.stats_min_label.pack(side="left", expand=True, pady=6)

        self.stats_avg_label = ctk.CTkLabel(stats_card, text="Avg: -- px", font=ctk.CTkFont(size=12, weight="bold"))
        self.stats_avg_label.pack(side="left", expand=True, pady=6)

        self.stats_max_label = ctk.CTkLabel(stats_card, text="Max: -- px", font=ctk.CTkFont(size=12))
        self.stats_max_label.pack(side="left", expand=True, pady=6)

        # Controls
        controls_card = ctk.CTkFrame(frame, corner_radius=12)
        controls_card.pack(fill="x", pady=5)

        self.thresh_label = ctk.CTkLabel(controls_card, text="Threshold: 40", font=ctk.CTkFont(size=12, weight="bold"))
        self.thresh_label.pack(pady=(4, 0))

        self.thresh_slider = ctk.CTkSlider(controls_card, from_=0, to=255, command=self.update_threshold_label)
        self.thresh_slider.set(40)
        self.thresh_slider.pack(fill="x", padx=12, pady=(0, 8))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(fill="x", pady=5)

        self.pause_btn = ctk.CTkButton(btn_row, text="⏸️ Pause", width=120, corner_radius=15, command=self.toggle_tracking)
        self.pause_btn.pack(side="left", expand=True, padx=5)

        self.export_btn = ctk.CTkButton(btn_row, text="💾 Export CSV", width=120, corner_radius=15, fg_color="#2e7d32", hover_color="#1b5e20", command=self.export_csv)
        self.export_btn.pack(side="right", expand=True, padx=5)

        return frame

    def create_guide_page(self):
        scroll_frame = ctk.CTkScrollableFrame(self.page_container, fg_color="transparent")

        ctk.CTkLabel(scroll_frame, text="Setup & Interpretation", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(5, 10))

        guides = [
            ("📡 ESP32-CAM Setup", "1. Flash the ESP32 code to your board.\n2. Open Serial Monitor at 115200 baud to find its IP address.\n3. Paste 'http://<ESP32_IP>/stream' into the Tracker connection box."),
            ("📏 Pupil Radius (Pixels)", "Measures distance from pupil center to perimeter. Values reflect current light intensity and eye response."),
            ("🎛️ Adjusting Threshold", "Move the threshold slider until the target pupil is surrounded by the green bounding circle without background noise.")
        ]

        for title, desc in guides:
            card = ctk.CTkFrame(scroll_frame, corner_radius=12)
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(10, 4))
            ctk.CTkLabel(card, text=desc, wraplength=340, justify="left", text_color="#bbbbbb").pack(anchor="w", padx=12, pady=(0, 10))

        return scroll_frame

    def create_about_page(self):
        frame = ctk.CTkFrame(self.page_container, fg_color="transparent")
        card = ctk.CTkFrame(frame, corner_radius=15)
        card.pack(fill="x", pady=10)

        ctk.CTkLabel(card, text="👁️ Pupil Metrics Studio", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(card, text="Version 3.0 (ESP32 Multi-Source)", font=ctk.CTkFont(size=12), text_color="#888888").pack(pady=(0, 15))

        tech_card = ctk.CTkFrame(frame, corner_radius=12)
        tech_card.pack(fill="x", pady=10)
        ctk.CTkLabel(tech_card, text="Supported Hardware", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(tech_card, text="• Standard USB Webcams\n• ESP32-CAM (AI-Thinker module)\n• IP Cameras serving MJPEG streams", justify="left", text_color="#aaaaaa").pack(anchor="w", padx=15, pady=(0, 12))

        return frame

    def change_camera_source(self):
        val = self.source_entry.get().strip()
        if val.isdigit():
            val = int(val)
        
        self.cap.release()
        self.camera_source = val
        self.cap = cv2.VideoCapture(self.camera_source)

    def update_threshold_label(self, value):
        self.thresh_label.configure(text=f"Threshold: {int(value)}")

    def toggle_tracking(self):
        self.is_tracking = not self.is_tracking
        if self.is_tracking:
            self.pause_btn.configure(text="⏸️ Pause", fg_color="#1f538d")
        else:
            self.pause_btn.configure(text="▶️ Resume", fg_color="#d32f2f")

    def export_csv(self):
        if not self.logged_data:
            return
        filename = f"pupil_data_{int(time.time())}.csv"
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp_Seconds", "Pupil_Radius_PX"])
            writer.writerows(self.logged_data)

    def update_frame(self):
        if self.is_tracking and self.current_page == "tracker":
            ret, frame = self.cap.read()
            if ret and frame is not None:
                frame = cv2.resize(frame, (360, 200))
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (7, 7), 0)

                thresh_val = int(self.thresh_slider.get())
                _, threshold = cv2.threshold(blurred, thresh_val, 255, cv2.THRESH_BINARY_INV)

                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                threshold = cv2.erode(threshold, kernel, iterations=1)
                threshold = cv2.dilate(threshold, kernel, iterations=2)

                contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                current_radius = 0
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    perimeter = cv2.arcLength(cnt, True)
                    if area > 100 and perimeter > 0:
                        circularity = 4 * np.pi * (area / (perimeter * perimeter))
                        if circularity > 0.5:
                            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
                            center = (int(cx), int(cy))
                            current_radius = int(radius)

                            cv2.circle(frame, center, current_radius, (0, 255, 0), 2)
                            cv2.circle(frame, center, 3, (0, 0, 255), -1)
                            cv2.putText(frame, f"R: {current_radius}px", (center[0] + 8, center[1] - 8),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                            break

                self.radius_history.append(current_radius)
                if len(self.radius_history) > self.history_len:
                    self.radius_history.pop(0)

                if current_radius > 0:
                    self.logged_data.append((round(time.time(), 2), current_radius))

                valid_radii = [r for r in self.radius_history if r > 0]
                if valid_radii:
                    self.stats_min_label.configure(text=f"Min: {min(valid_radii)} px")
                    self.stats_avg_label.configure(text=f"Avg: {int(sum(valid_radii)/len(valid_radii))} px")
                    self.stats_max_label.configure(text=f"Max: {max(valid_radii)} px")

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(rgb_frame)
                img_tk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(360, 200))
                self.video_label.configure(image=img_tk, text="")

                graph_img = np.full((110, 360, 3), 30, dtype=np.uint8)
                cv2.line(graph_img, (0, 105), (360, 105), (70, 70, 70), 1)

                graph_x_start = 5
                graph_y_base = 100

                for i in range(1, len(self.radius_history)):
                    if self.radius_history[i-1] > 0 and self.radius_history[i] > 0:
                        x1 = graph_x_start + int((i - 1) * 3.5)
                        y1 = graph_y_base - (self.radius_history[i - 1] * 2)
                        
                        x2 = graph_x_start + int(i * 3.5)
                        y2 = graph_y_base - (self.radius_history[i] * 2)
                        
                        cv2.line(graph_img, (x1, y1), (x2, y2), (0, 230, 150), 2)

                rgb_graph = cv2.cvtColor(graph_img, cv2.COLOR_BGR2RGB)
                graph_pil = Image.fromarray(rgb_graph)
                graph_tk = ctk.CTkImage(light_image=graph_pil, dark_image=graph_pil, size=(360, 110))
                self.graph_label.configure(image=graph_tk, text="")

        self.after(16, self.update_frame)

    def on_closing(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = MobilePupilApp()
    app.mainloop()