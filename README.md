# Digha Science Centre – Show Announcement System

An automated and manual audio announcement management system built with Python, CustomTkinter, and Pygame for the **Digha Science Centre & National Science Camp** (under National Council of Science Museums, Ministry of Culture, Govt. of India).

---

## 📁 Project Directory Structure

```text
DSC-Announcement-System/
├── audio/                      # All 94 MP3 announcement audio files
│   ├── 3D Show Call For Show_*.mp3
│   ├── 3D Show Call For Ticket_*.mp3
│   ├── Fun Science Show Call For Show_*.mp3
│   ├── Fun Science Show Call For Ticket_*.mp3
│   ├── Space & Astronomy Call For Show_*.mp3
│   ├── Space & Astronomy Call For Ticket_*.mp3
│   ├── Taramandal Show Call for Show_*.mp3
│   └── Taramandal Show Call for Ticket_*.mp3
├── assets/                     # Graphical assets (icon, logo, background)
│   ├── logo.ico
│   ├── logo1.png
│   └── bg.jpg
├── main.py                     # Primary application entrypoint
├── UI_3O.py                    # Backward compatibility launcher
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── .gitignore                  # Git ignore rules
```

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10 or 3.11 (Python 3.11 recommended on Windows)
- Required packages:
  ```powershell
  pip install -r requirements.txt
  ```

### 2. Running the Application
Launch via Python 3.11:
```powershell
py -3.11 main.py
```
*(Or `py -3.11 UI_3O.py`)*

---

## 🔐 Login Access

- **Security PIN**: `721463` (Postal Code of Digha Science Centre)
- Enter via physical keyboard or the on-screen touch numpad.

---

## ✨ Features

- **Sequential Audio Queue**: Enqueue multiple show announcements seamlessly in a background worker thread without freezing the UI.
- **Autopilot Mode**: Automated real-time scheduler triggering ticket booking announcements (15m & 10m before show time) and show entry announcements (5m before show time).
- **Live Digital Clock**: Real-time 24-hour synchronized clock display.
- **Audio Progress Bar**: Shows current playback position and total track length in `MM:SS / MM:SS`.
- **Animated Audio Visualizer**: 20-segment 3-color simulated VU LED meter active during playback.
- **Dark / Light Theme Switcher**: Instant aesthetic toggle.
- **Full Screen Toggle**: One-click borderless kiosk mode or windowed mode (`Esc` key shortcut).
