import customtkinter as ctk
import pygame
import threading
import queue
import datetime
import time
import os

# -------------------- INITIAL SETUP --------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

pygame.mixer.init()

app = ctk.CTk()
app.title("Digha Science Centre – Announcement System")

# -------------------- FULLSCREEN FIX --------------------

app.update_idletasks()

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

app.geometry(f"{screen_width}x{screen_height}+0+0")
app.overrideredirect(True)  # Removes title bar & border

def exit_fullscreen(event=None):
    app.overrideredirect(False)
    app.geometry("1200x800")

app.bind("<Escape>", exit_fullscreen)

# -------------------- GLOBAL STATE --------------------

audio_queue = queue.Queue()
is_playing = False
current_playing_file = None
queued_files = []

buttons_map = {}

current_playing_var = ctk.StringVar(value="Idle")
queue_status_var = ctk.StringVar(value="Queue: 0")

# -------------------- BUTTON COLORS --------------------

NORMAL_COLOR = "#1f6aa5"
QUEUE_COLOR = "#aa7d00"
PLAY_COLOR_1 = "#00aa55"
PLAY_COLOR_2 = "#00ff88"

blink_state = False

# -------------------- BUTTON VISUAL UPDATE --------------------

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
        color = PLAY_COLOR_1 if blink_state else PLAY_COLOR_2
        btn.configure(fg_color=color)
        blink_state = not blink_state

    app.after(500, blink_playing_button)

blink_playing_button()

# -------------------- QUEUE DISPLAY --------------------

def update_queue_display():
    total = audio_queue.qsize()
    if is_playing:
        total += 1
    queue_status_var.set(f"Queue: {total}")
    update_button_states()

# -------------------- AUDIO ENGINE --------------------

def audio_worker():
    global is_playing, current_playing_file

    while True:
        file_path = audio_queue.get()
        if file_path is None:
            break

        try:
            is_playing = True
            current_playing_file = file_path

            if file_path in queued_files:
                queued_files.remove(file_path)

            update_queue_display()

            current_playing_var.set(f"Playing: {os.path.basename(file_path)}")

            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.3)

        except:
            current_playing_var.set("Error Playing File")

        is_playing = False
        current_playing_file = None
        audio_queue.task_done()
        update_queue_display()
        current_playing_var.set("Idle")

threading.Thread(target=audio_worker, daemon=True).start()

# -------------------- PLAY FUNCTION --------------------

def enqueue_audio(show, time_slot):
    time_slot_new = time_slot.replace(":", "")
    file_name = f"{show}_{time_slot_new}.mp3"

    if os.path.exists(file_name):
        audio_queue.put(file_name)
        queued_files.append(file_name)
        update_queue_display()
    else:
        current_playing_var.set("File Not Found")

def stop_audio():
    global is_playing, current_playing_file

    pygame.mixer.music.stop()
    is_playing = False
    current_playing_file = None

    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
            audio_queue.task_done()
        except:
            break

    queued_files.clear()
    update_queue_display()
    current_playing_var.set("Stopped")

# -------------------- TOP BAR --------------------

top_frame = ctk.CTkFrame(app, height=80)
top_frame.pack(fill="x", pady=10, padx=20)

title_label = ctk.CTkLabel(
    top_frame,
    text="Digha Science Centre – Announcement Control Panel",
    font=("Arial", 28, "bold")
)
title_label.pack(side="left", padx=20)

clock_var = ctk.StringVar()

def update_clock():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    clock_var.set(now)
    app.after(1000, update_clock)

clock_label = ctk.CTkLabel(top_frame, textvariable=clock_var, font=("Arial", 24))
clock_label.pack(side="right", padx=20)

update_clock()

# -------------------- SHOW DATA --------------------

show_times = {
    "Space & Astronomy Call For Show": ["09:30 AM","10:30 AM","11:30 AM","12:00 NOON","12:30 PM",
                                       "02:00 PM","03:00 PM","04:00 PM","04:30 PM","05:00 PM",
                                       "05:30 PM","06:00 PM","06:30 PM","07:00 PM"],

    "Space & Astronomy Call For Ticket": ["09:30 AM","10:30 AM","11:30 AM","12:00 NOON","12:30 PM",
                                         "02:00 PM","03:00 PM","04:00 PM","04:30 PM","05:00 PM",
                                         "05:30 PM","06:00 PM","06:30 PM","07:00 PM"],

    "3D Show Call For Show": ["09:00 AM","10:00 AM","11:00 AM","12:00 NOON","12:30 PM",
                              "02:00 PM","03:30 PM","04:00 PM","04:30 PM","05:00 PM",
                              "05:30 PM","06:00 PM","06:30 PM","07:00 PM"],

    "3D Show Call For Ticket": ["09:00 AM","10:00 AM","11:00 AM","12:00 NOON","12:30 PM",
                                "02:00 PM","03:30 PM","04:00 PM","04:30 PM","05:00 PM",
                                "05:30 PM","06:00 PM","06:30 PM","07:00 PM"],

    "Fun Science Show Call For Show": ["12:00 NOON","01:00 PM","03:00 PM","04:00 PM",
                                       "05:00 PM","06:00 PM","07:00 PM"],

    "Fun Science Show Call For Ticket": ["12:00 NOON","01:00 PM","03:00 PM","04:00 PM",
                                         "05:00 PM","06:00 PM","07:00 PM"],
}

# -------------------- MAIN GRID --------------------

main_frame = ctk.CTkFrame(app)
main_frame.pack(expand=True, fill="both", padx=20, pady=10)

rows = 2
cols = 3

for r in range(rows):
    main_frame.grid_rowconfigure(r, weight=1)
for c in range(cols):
    main_frame.grid_columnconfigure(c, weight=1)

sections = list(show_times.items())

for index, (show, times) in enumerate(sections):
    row = index // cols
    col = index % cols

    section_frame = ctk.CTkFrame(main_frame, corner_radius=15)
    section_frame.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)

    section_label = ctk.CTkLabel(
        section_frame,
        text=show,
        font=("Arial", 18, "bold")
    )
    section_label.pack(pady=10)

    button_frame = ctk.CTkFrame(section_frame)
    button_frame.pack(expand=True, fill="both", padx=10, pady=10)

    for i in range(4):
        button_frame.grid_columnconfigure(i, weight=1)

    for i, time_slot in enumerate(times):
        r = i // 4
        c = i % 4

        time_slot_new = time_slot.replace(":", "")
        file_name = f"{show}_{time_slot_new}.mp3"

        btn = ctk.CTkButton(
            button_frame,
            text=time_slot,
            height=65,
            font=("Arial", 16, "bold"),
            fg_color=NORMAL_COLOR,
            command=lambda s=show, t=time_slot: enqueue_audio(s, t)
        )
        btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

        buttons_map[file_name] = btn

# -------------------- STATUS BAR --------------------

bottom_frame = ctk.CTkFrame(app, height=80)
bottom_frame.pack(fill="x", padx=20, pady=10)

status_label = ctk.CTkLabel(
    bottom_frame,
    textvariable=current_playing_var,
    font=("Arial", 20, "bold")
)
status_label.pack(side="left", padx=20)

queue_label = ctk.CTkLabel(
    bottom_frame,
    textvariable=queue_status_var,
    font=("Arial", 20)
)
queue_label.pack(side="left", padx=20)

stop_button = ctk.CTkButton(
    bottom_frame,
    text="STOP",
    fg_color="red",
    hover_color="#8B0000",
    height=65,
    width=220,
    font=("Arial", 20, "bold"),
    command=stop_audio
)
stop_button.pack(side="right", padx=20)

app.mainloop()