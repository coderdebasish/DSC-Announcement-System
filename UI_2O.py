import customtkinter as ctk
import pygame
import threading
import queue
import datetime
import time
import os

# =========================================================
# INITIAL SETUP
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

pygame.mixer.init()

app = ctk.CTk()
app.title("Digha Science Centre – Announcement System")

# -------- FULLSCREEN --------
app.update_idletasks()
w = app.winfo_screenwidth()
h = app.winfo_screenheight()
app.geometry(f"{w}x{h}+0+0")
app.overrideredirect(True)

def exit_fullscreen(event=None):
    app.overrideredirect(False)
    app.geometry("1200x800")

app.bind("<Escape>", exit_fullscreen)

# =========================================================
# GLOBAL STATE
# =========================================================

audio_queue = queue.Queue()
queued_files = []
buttons_map = {}

is_playing = False
current_playing_file = None

autopilot_mode = False
last_checked_minute = None
session_triggered_events = set()

theme_mode = "dark"

current_playing_var = ctk.StringVar(value="Idle")
queue_status_var = ctk.StringVar(value="Queue: 0")
clock_var = ctk.StringVar()

# =========================================================
# THREAD SAFE UI
# =========================================================

def safe_ui(func, *args):
    app.after(0, func, *args)

# =========================================================
# BUTTON COLORS
# =========================================================

NORMAL_COLOR = "#1f6aa5"
QUEUE_COLOR = "#aa7d00"
PLAY_COLOR_1 = "#00aa55"
PLAY_COLOR_2 = "#00ff88"

blink_state = False

def update_button_states():
    for file_name, btn in buttons_map.items():
        if file_name == current_playing_file:
            continue
        elif file_name in queued_files:
            btn.configure(fg_color=QUEUE_COLOR)
        else:
            btn.configure(fg_color=NORMAL_COLOR)

def blink_playing_button():
    global blink_state
    if current_playing_file and current_playing_file in buttons_map:
        btn = buttons_map[current_playing_file]
        btn.configure(
            fg_color=PLAY_COLOR_1 if blink_state else PLAY_COLOR_2
        )
        blink_state = not blink_state
    app.after(500, blink_playing_button)

blink_playing_button()

def update_queue_display():
    total = audio_queue.qsize()
    if is_playing:
        total += 1
    queue_status_var.set(f"Queue: {total}")
    update_button_states()

# =========================================================
# AUDIO ENGINE
# =========================================================

def audio_worker():
    global is_playing, current_playing_file

    while True:
        file_path = audio_queue.get()

        try:
            is_playing = True
            current_playing_file = file_path

            if file_path in queued_files:
                queued_files.remove(file_path)

            safe_ui(update_queue_display)
            safe_ui(current_playing_var.set,
                    f"Playing: {os.path.basename(file_path)}")

            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.2)

        except:
            safe_ui(current_playing_var.set, "Error Playing File")

        is_playing = False
        current_playing_file = None
        audio_queue.task_done()

        safe_ui(update_queue_display)
        safe_ui(current_playing_var.set, "Idle")

threading.Thread(target=audio_worker, daemon=True).start()

# =========================================================
# PLAY FUNCTIONS
# =========================================================

def enqueue_audio(show, time_slot):
    time_slot_new = time_slot.replace(":", "")
    file_name = f"{show}_{time_slot_new}.mp3"

    if os.path.exists(file_name):
        audio_queue.put(file_name)
        queued_files.append(file_name)
        update_queue_display()

def stop_audio():
    global is_playing, current_playing_file

    pygame.mixer.music.stop()
    is_playing = False
    current_playing_file = None

    while not audio_queue.empty():
        audio_queue.get_nowait()
        audio_queue.task_done()

    queued_files.clear()
    update_queue_display()
    current_playing_var.set("Stopped")

# =========================================================
# CLOCK
# =========================================================

def update_clock():
    now = datetime.datetime.now()
    clock_var.set(now.strftime("%H:%M:%S"))
    delay = 1000 - now.microsecond // 1000
    app.after(delay, update_clock)

update_clock()

# =========================================================
# AUTOPILOT ENGINE (FIXED 15 + 10 MIN)
# =========================================================

def parse_show_time(time_str):
    if "NOON" in time_str:
        return datetime.datetime.strptime("12:00 PM", "%I:%M %p").time()
    return datetime.datetime.strptime(time_str, "%I:%M %p").time()

def autopilot_scheduler():
    global last_checked_minute

    while True:
        if autopilot_mode:

            now = datetime.datetime.now()
            current_minute = now.strftime("%Y-%m-%d %H:%M")

            if current_minute != last_checked_minute:
                last_checked_minute = current_minute

                today = now.date()
                current_time = now.replace(second=0, microsecond=0)

                for show, times in show_times.items():
                    for time_slot in times:

                        show_time = parse_show_time(time_slot)
                        show_dt = datetime.datetime.combine(today, show_time)

                        trigger_map = []

                        if "Ticket" in show:
                            trigger_map = [
                                ("15min", show_dt - datetime.timedelta(minutes=15)),
                                ("10min", show_dt - datetime.timedelta(minutes=10))
                            ]

                        if "Show" in show and "Ticket" not in show:
                            trigger_map = [
                                ("5min", show_dt - datetime.timedelta(minutes=5))
                            ]

                        for trigger_type, trigger_time in trigger_map:
                            if trigger_time == current_time:

                                time_slot_new = time_slot.replace(":", "")
                                file_name = f"{show}_{time_slot_new}.mp3"

                                event_key = (file_name, trigger_type)

                                if event_key not in session_triggered_events:
                                    session_triggered_events.add(event_key)

                                    if os.path.exists(file_name):
                                        audio_queue.put(file_name)
                                        queued_files.append(file_name)
                                        safe_ui(update_queue_display)

        time.sleep(1)

threading.Thread(target=autopilot_scheduler, daemon=True).start()

# =========================================================
# BUTTON ACTIONS
# =========================================================

def toggle_autopilot():
    global autopilot_mode, session_triggered_events
    autopilot_mode = not autopilot_mode
    session_triggered_events.clear()

    if autopilot_mode:
        autopilot_button.configure(text="AUTOPILOT: ON", fg_color="green")
    else:
        autopilot_button.configure(text="AUTOPILOT: OFF", fg_color="red")

def toggle_theme():
    global theme_mode

    if theme_mode == "dark":
        theme_mode = "light"
        ctk.set_appearance_mode("light")
        theme_button.configure(text="LIGHT MODE")
    else:
        theme_mode = "dark"
        ctk.set_appearance_mode("dark")
        theme_button.configure(text="DARK MODE")

# =========================================================
# UI LAYOUT
# =========================================================

top_frame = ctk.CTkFrame(app, height=80)
top_frame.pack(fill="x", pady=10, padx=20)

ctk.CTkLabel(
    top_frame,
    text="Digha Science Centre – Announcement Control Panel",
    font=("Arial", 28, "bold")
).pack(side="left", padx=20)

ctk.CTkLabel(
    top_frame,
    textvariable=clock_var,
    font=("Arial", 24)
).pack(side="right", padx=20)

theme_button = ctk.CTkButton(
    top_frame,
    text="DARK MODE",
    width=160,
    height=55,
    font=("Arial", 16, "bold"),
    command=toggle_theme
)
theme_button.pack(side="right", padx=10)

autopilot_button = ctk.CTkButton(
    top_frame,
    text="AUTOPILOT: OFF",
    width=220,
    height=55,
    fg_color="red",
    command=toggle_autopilot
)
autopilot_button.pack(side="right", padx=10)

# =========================================================
# SHOW DATA
# =========================================================

show_times = {
    "Space & Astronomy Call For Ticket": [
        "09:30 AM","10:30 AM","11:30 AM","12:00 NOON","12:30 PM",
        "02:00 PM","03:00 PM","04:00 PM","04:30 PM","05:00 PM",
        "05:30 PM","06:00 PM","06:30 PM","07:00 PM"
    ],

    "Space & Astronomy Call For Show": [
        "09:30 AM","10:30 AM","11:30 AM","12:00 NOON","12:30 PM",
        "02:00 PM","03:00 PM","04:00 PM","04:30 PM","05:00 PM",
        "05:30 PM","06:00 PM","06:30 PM","07:00 PM"
    ],

    "3D Show Call For Ticket": [
        "09:00 AM","10:00 AM","11:00 AM","12:00 NOON","12:30 PM",
        "02:00 PM","03:30 PM","04:00 PM","04:30 PM","05:00 PM",
        "05:30 PM","06:00 PM","06:30 PM","07:00 PM"
    ],

    "3D Show Call For Show": [
        "09:00 AM","10:00 AM","11:00 AM","12:00 NOON","12:30 PM",
        "02:00 PM","03:30 PM","04:00 PM","04:30 PM","05:00 PM",
        "05:30 PM","06:00 PM","06:30 PM","07:00 PM"
    ],

    "Fun Science Show Call For Ticket": [
        "12:00 NOON","01:00 PM","03:00 PM","04:00 PM",
        "05:00 PM","06:00 PM","07:00 PM"
    ],

    "Fun Science Show Call For Show": [
        "12:00 NOON","01:00 PM","03:00 PM","04:00 PM",
        "05:00 PM","06:00 PM","07:00 PM"
    ],
}

# -------- Layout (Tickets Top Row, Shows Bottom Row) --------

ticket_sections = [k for k in show_times if "Ticket" in k]
show_sections = [k for k in show_times if "Show" in k and "Ticket" not in k]

main_frame = ctk.CTkFrame(app)
main_frame.pack(expand=True, fill="both", padx=20, pady=10)

main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)

for i in range(3):
    main_frame.grid_columnconfigure(i, weight=1)

def create_section(row, col, show):
    frame = ctk.CTkFrame(main_frame, corner_radius=15)
    frame.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)

    ctk.CTkLabel(frame, text=show, font=("Arial", 18, "bold")).pack(pady=10)

    button_frame = ctk.CTkFrame(frame)
    button_frame.pack(expand=True, fill="both", padx=10, pady=10)

    for i in range(4):
        button_frame.grid_columnconfigure(i, weight=1)

    for i, time_slot in enumerate(show_times[show]):
        r = i // 4
        c = i % 4
        time_slot_new = time_slot.replace(":", "")
        file_name = f"{show}_{time_slot_new}.mp3"

        btn = ctk.CTkButton(
            button_frame,
            text=time_slot,
            height=60,
            fg_color=NORMAL_COLOR,
            command=lambda s=show, t=time_slot: enqueue_audio(s, t)
        )
        btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

        buttons_map[file_name] = btn

for i, section in enumerate(ticket_sections):
    create_section(0, i, section)

for i, section in enumerate(show_sections):
    create_section(1, i, section)

# =========================================================
# STATUS BAR
# =========================================================

bottom_frame = ctk.CTkFrame(app, height=80)
bottom_frame.pack(fill="x", padx=20, pady=10)

ctk.CTkLabel(bottom_frame,
             textvariable=current_playing_var,
             font=("Arial", 20, "bold")
             ).pack(side="left", padx=20)

ctk.CTkLabel(bottom_frame,
             textvariable=queue_status_var,
             font=("Arial", 20)
             ).pack(side="left", padx=20)

ctk.CTkButton(
    bottom_frame,
    text="STOP",
    fg_color="red",
    height=60,
    width=200,
    font=("Arial", 20, "bold"),
    command=stop_audio
).pack(side="right", padx=20)

app.mainloop()