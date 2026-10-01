# 👁️ Pupil Metrics Studio (Mobile Edition)

A lightweight, real-time pupil detection and ocular metric analysis application styled as a modern mobile smartphone interface. Built with **Python**, **OpenCV**, **CustomTkinter**, and **NumPy**.

![App Style](<img width="530" height="1020" alt="Screenshot 2026-09-29 203852" src="https://github.com/user-attachments/assets/15352229-cc35-43b2-8989-d813dbb493e4" />)
![Python](<img width="1916" height="1136" alt="Screenshot 2026-09-29 202144" src="https://github.com/user-attachments/assets/a1715e7e-24c4-4ce7-b833-1209c7ffdac1" />)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-orange)
![License](https://img.shields.io/badge/License-MIT-brightgreen)

---

## 🏗️ System & Physical Architecture

The diagram below illustrates how hardware input streams through the software pipeline to render live metrics on the UI and export data.

```
==================================================================================
1. PHYSICAL & HARDWARE LAYER
==================================================================================

  [ USB Webcam / Laptop Camera ] ──( USB 2.0/3.0 Bus )──┐
                                                       ├──> [ Host Computer ]
  [ ESP32-CAM Eye Tracking Rig ] ──( Wi-Fi / Serial COM )┘


==================================================================================
2. SOFTWARE PIPELINE & DATA FLOW
==================================================================================

                        ┌──────────────────────────────┐
                        │ cv2.VideoCapture(0 / Stream) │
                        └──────────────┬───────────────┘
                                       │ Raw BGR Frames (60 FPS)
                                       v
                        ┌──────────────────────────────┐
                        │     Image Preprocessing      │
                        │ ──> cv2.cvtColor (Grayscale) │
                        │ ──> GaussianBlur (7x7)       │
                        └──────────────┬───────────────┘
                                       │
                                       v
                        ┌──────────────────────────────┐
                        │     Adaptive Thresholding    │
                        │ ──> Threshold Slider (0-255) │
                        │ ──> Morphological Erode/Dilate│
                        └──────────────┬───────────────┘
                                       │
                                       v
                        ┌──────────────────────────────┐
                        │   Contour & Circle Engine    │
                        │ ──> cv2.findContours         │
                        │ ──> Circularity Filter (>0.5)│
                        │ ──> cv2.minEnclosingCircle   │
                        └──────────────┬───────────────┘
                                       │
                         Calculated Radius (px)
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            │                                                     │
            v                                                     v
┌───────────────────────────────┐                     ┌────────────────────────┐
│    UI & Canvas Render Engine  │                     │   Analytics & Storage  │
├───────────────────────────────┤                     ├────────────────────────┤
│ • NumPy Canvas Graph Trace    │                     │ • Live Min / Avg / Max │
│ • Pillow PIL RGB Conversion   │                     │ • Time-stamped Log     │
│ • CustomTkinter CTkImage      │                     │ • CSV Exporter         │
└──────────────┬────────────────┘                     └───────────┬────────────┘
               │                                                  │
               v                                                  v
┌──────────────────────────────────────────────────────────────────────────────┐
│                    MOBILE UI SCREEN CONTAINER (420x780)                      │
├─────────────────┬───────────────────┬────────────────────┬───────────────────┤
│ 🏠 Home Screen  │ 👁️ Tracker View   │ 📊 Interpre. Guide │ ℹ️️ About & Tech   │
└─────────────────┴───────────────────┴────────────────────┴───────────────────┘
```

---

## ✨ Key Features

- **📱 Mobile App UX:** Vertical portrait design featuring a bottom navigation bar for quick access across four screens:
  - **Home Screen:** Overview and quick launch.
  - **Tracker Screen:** Main camera feed, graph, live stats, and controls.
  - **Guide Screen:** Detailed instructions on tuning thresholds and reading pupil dilation metrics.
  - **About Screen:** Tech stack overview and version information.
- **👁️ Real-Time Pupil Detection:** High-speed contour detection that isolates round shapes using a mathematical circularity filter (`4 * pi * Area / Perimeter^2 > 0.5`).
- **📈 Real-Time Graphing:** Direct array-to-image line drawing using OpenCV, eliminating Matplotlib system lag.
- **📊 Live Statistics:** Real-time computation of **Minimum**, **Average**, and **Maximum** pupil radius in pixels.
- **⏸️ Pause & Resume:** Freeze frame capture to examine eye state without closing the camera stream.
- **💾 CSV Export:** Log time-stamped pupil radius measurements directly to a `.csv` file for research and plotting.

---

## 🛠️ Tech Stack

- **GUI Framework:** CustomTkinter
- **Computer Vision:** OpenCV (`opencv-python`)
- **Array & Image Processing:** NumPy & Pillow (PIL)
- **Language:** Python 3.8+

---

## 🚀 Installation & Usage

### 1. Install Dependencies
```bash
pip install customtkinter opencv-python pillow numpy
```

### 2. Run the Application
```bash
python mobile_pupil_app.py
```

---

## 🎛️ How to Calibrate Tracking

1. Launch the app and switch to the **👁️ Tracker** tab.
2. Position your camera facing the eye with consistent lighting.
3. Move the **Threshold Slider** until the green circle tightly bounds the pupil without picking up eyelashes or shadows.
4. Press **⏸️ Pause** to lock the current frame, or click **💾 Export CSV** to save your tracking session data.

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
