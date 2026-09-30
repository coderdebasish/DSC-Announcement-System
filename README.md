# Digha Science Centre – Show Announcement System

An automated and manual audio announcement management system built with Python, CustomTkinter, and Pygame for the **Digha Science Centre & National Science Camp** (under National Council of Science Museums, Ministry of Culture, Govt. of India).

---

## 📁 Project Directory Structure

```text
DSC-Announcement-System/
├── audio/                      # All MP3 announcement audio files
│   ├── 3D Show Call For Show_*.mp3
│   ├── 3D Show Call For Ticket_*.mp3
│   ├── Fun Science Show Call For Show_*.mp3
│   ├── Fun Science Show Call For Ticket_*.mp3
│   ├── Space & Astronomy Call For Show_*.mp3
│   └── Space & Astronomy Call For Ticket_*.mp3
├── assets/                     # Graphic assets (icon, logo, background)
│   ├── logo.ico
│   ├── logo1.png
│   └── bg.jpg
├── schedule.db                 # Local SQLite database storing all show time slots
├── database.py                 # SQLite database helper and audio file manager
├── main.py                     # Primary application entrypoint
├── UI.py                       # Compatibility launcher
├── UI_3O.py                    # Compatibility launcher
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
*(Or `py -3.11 UI.py` / `py -3.11 UI_3O.py`)*

---

## 🔐 Login Access

- **Security PIN**: `721463` (Postal Code of Digha Science Centre)
- Enter via physical keyboard or the on-screen touch numpad.

---

## ✨ Features

- **⚙ Dynamic Show & Slot Manager**:
  - No need to edit Python code to change the schedule.
  - Click **⚙ MANAGE SLOTS** on the top navigation bar.
  - **Add New Slot**: Pick the show, pick or type the time slot (e.g. `02:30 PM`), and attach any `.mp3` or `.wav` file. The app automatically copies the file into `audio/` with the standard name format and adds it to `schedule.db`.
  - **View & Remove Slots**: Inspect all existing slots, listen to live audio previews, attach/replace audio recordings, or delete any slot (with an option to delete the MP3 file from disk).
  - Main dashboard grid updates dynamically in real time.
- **Scrollable Unlimited Slots**: Each show section features a scrollable frame so any number of slots can be added without UI overflow or clipping.
- **Sequential Audio Queue**: Enqueue multiple show announcements seamlessly in a background worker thread.
- **Autopilot Mode**: Automated real-time scheduler triggering ticket booking announcements (15m & 10m before show time) and show entry announcements (5m before show time), reading dynamically from `schedule.db`.
- **Live Digital Clock**: Real-time 24-hour synchronized clock display.
- **Audio Progress Bar**: Shows current playback position and total track length in `MM:SS / MM:SS`.
- **Animated Audio Visualizer**: 20-segment 3-color simulated VU LED meter active during playback.
- **Dark / Light Theme Switcher**: Instant aesthetic toggle.
- **Full Screen Toggle**: One-click borderless kiosk mode or windowed mode (`Esc` key shortcut).
