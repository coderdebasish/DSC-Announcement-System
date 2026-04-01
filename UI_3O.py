import customtkinter as ctk
import pygame
import threading
import datetime
import time
import os
import random
from mutagen.mp3 import MP3

# =========================================================
# LOGIN SYSTEM
# =========================================================

CORRECT_CODE = "721463"

def start_login():

    ctk.deactivate_automatic_dpi_awareness()

    login_app = ctk.CTk()

    # Center the window on screen
    screen_width = login_app.winfo_screenwidth()
    screen_height = login_app.winfo_screenheight()
    window_width = 600
    window_height = 700
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    login_app.geometry(f"{window_width}x{window_height}+{x}+{y}")
    login_app.focus_force()

    login_app.title("Login Panel")

    login_app.protocol("WM_DELETE_WINDOW", lambda: exit())

    ctk.CTkLabel(login_app,
        text="Digha Science Centre – Announcement System",
        font=("Arial", 20, "bold")
    ).pack(pady=20)

    ctk.CTkLabel(login_app,
        text="Enter 6 Digit Code",
        font=("Arial", 18)
    ).pack(pady=20)

    code_entry = ctk.CTkEntry(login_app,
        width=200, height=40, show="*", justify="center")
    code_entry.pack(pady=10)
    code_entry.focus()
    code_entry.configure(insertontime=0)
    
    show_btn = ctk.CTkButton(login_app, text="👁", width=35, height=35, command=lambda: toggle_show())
    show_btn.pack(pady=2)

    def toggle_show():
        if code_entry.cget("show") == "*":
            code_entry.configure(show="")
            show_btn.configure(text="🙈")
        else:
            code_entry.configure(show="*")
            show_btn.configure(text="👁")

    error_label = ctk.CTkLabel(login_app, text="", text_color="red")
    error_label.pack()

    def validate_input(text):
        return text.isdigit() or text == ""

    vcmd = (login_app.register(validate_input), "%P")
    code_entry.configure(validate="key", validatecommand=vcmd)

    def check_code():
        if code_entry.get() == CORRECT_CODE:
            # Clear login widgets and proceed to main app
            for widget in login_app.winfo_children():
                widget.destroy()
            login_app.title("Digha Science Centre – Announcement System")
            open_main_app(login_app)
        else:
            error_label.configure(text="Incorrect Code ❌")
            code_entry.delete(0, 'end')

    login_app.bind("<Return>", lambda e: check_code())

    ctk.CTkButton(login_app,
        text="Login",
        width=180,
        height=45,
        fg_color="green",
        command=check_code
    ).pack(pady=20)

    # Numeric Keyboard
    keyboard_frame = ctk.CTkFrame(login_app)
    keyboard_frame.pack(pady=5, padx=20)

    # Define button layout
    keys = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9'],
        ['⌫', '0', 'Enter']
    ]

    def key_press(key):
        if key == '⌫':
            current = code_entry.get()
            if current:
                code_entry.delete(len(current)-1, 'end')
        elif key == 'Enter':
            check_code()
        else:
            code_entry.insert('end', key)

    for row_idx, row in enumerate(keys):
        for col_idx, key in enumerate(row):
            if key == '⌫':
                color = "#FF5722"
                hover = "#D84315"
            elif key == 'Enter':
                color = "#4CAF50"
                hover = "#388E3C"
            else:
                color = "#2196F3"
                hover = "#1976D2"
            btn = ctk.CTkButton(
                keyboard_frame,
                text=key,
                width=70,
                height=70,
                fg_color=color,
                hover_color=hover,
                corner_radius=10,
                text_color="white",
                font=("Arial", 20),
                command=lambda k=key: key_press(k)
            )
            btn.grid(row=row_idx, column=col_idx, padx=8, pady=8)

    login_app.mainloop()


# =========================================================
# MAIN APP
# =========================================================

def open_main_app(app):

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    pygame.mixer.init()

    # FULLSCREEN STATE
    is_fullscreen = True

    app.update_idletasks()
    w = app.winfo_screenwidth()
    h = app.winfo_screenheight()
    app.geometry(f"{w}x{h}+0+0")
    app.overrideredirect(True)

    app.protocol("WM_DELETE_WINDOW", lambda: app.destroy())

    def toggle_fullscreen():
        nonlocal is_fullscreen

        if is_fullscreen:
            app.overrideredirect(False)
            app.geometry("1200x800")
            fullscreen_btn.configure(text="Enter Full Screen", fg_color="green")
            is_fullscreen = False
        else:
            app.overrideredirect(True)
            app.geometry(f"{w}x{h}+0+0")
            fullscreen_btn.configure(text="Exit Full Screen", fg_color="red")
            is_fullscreen = True

    app.bind("<Escape>", lambda e: toggle_fullscreen())

    # =====================================================
    # GLOBAL STATE
    # =====================================================

    audio_queue = []
    buttons_map = {}

    is_playing = False
    current_playing_file = None
    current_length = 0

    autopilot_mode = False
    last_checked_minute = None
    session_triggered_events = set()

    theme_mode = "dark"

    NORMAL_COLOR = "#1f6aa5"
    QUEUE_COLOR = "#aa7d00"
    PLAY_COLOR_1 = "#00aa55"
    PLAY_COLOR_2 = "#00ff88"

    GREEN = "#00c853"
    YELLOW = "#ffd600"
    RED = "#d50000"
    INACTIVE = "#3a3a3a"

    blink_state = False
    fake_level = 0

    current_playing_var = ctk.StringVar(value="Idle")
    queue_status_var = ctk.StringVar(value="Queue: 0")
    clock_var = ctk.StringVar()

    progress_var = ctk.DoubleVar(value=0)
    progress_text_var = ctk.StringVar(value="00:00 / 00:00")

    # =====================================================
    # SAFE UI
    # =====================================================

    def safe_ui(func, *args):
        app.after(0, func, *args)

    # =====================================================
    # BUTTON STATES
    # =====================================================

    def update_button_states():
        for file_name, btn in buttons_map.items():
            if file_name == current_playing_file:
                continue
            elif file_name in audio_queue:
                btn.configure(fg_color=QUEUE_COLOR)
            else:
                btn.configure(fg_color=NORMAL_COLOR)

    def blink_playing_button():
        nonlocal blink_state
        if current_playing_file in buttons_map:
            btn = buttons_map[current_playing_file]
            btn.configure(fg_color=PLAY_COLOR_1 if blink_state else PLAY_COLOR_2)
            blink_state = not blink_state
        app.after(500, blink_playing_button)

    blink_playing_button()

    def update_queue_display():
        total = len(audio_queue)
        if is_playing:
            total += 1
        queue_status_var.set(f"Queue: {total}")
        update_button_states()

    # =====================================================
    # AUDIO ENGINE
    # =====================================================

    def audio_worker():
        nonlocal is_playing, current_playing_file, current_length

        while True:
            if not audio_queue:
                time.sleep(0.1)
                continue

            file_path = audio_queue.pop(0)

            try:
                is_playing = True
                current_playing_file = file_path

                audio = MP3(file_path)
                current_length = int(audio.info.length)

                safe_ui(update_queue_display)
                safe_ui(current_playing_var.set,
                        f"Playing: {os.path.basename(file_path)}")

                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

            except:
                safe_ui(current_playing_var.set, "Error Playing File")

            is_playing = False
            current_playing_file = None

            safe_ui(update_queue_display)
            safe_ui(current_playing_var.set, "Idle")

    threading.Thread(target=audio_worker, daemon=True).start()

    # =====================================================
    # CLOCK
    # =====================================================

    def update_clock():
        clock_var.set(datetime.datetime.now().strftime("%H:%M:%S"))
        app.after(1000, update_clock)

    update_clock()

    # =====================================================
    # AUTOPILOT
    # =====================================================

    def parse_show_time(time_str):
        if "NOON" in time_str:
            return datetime.datetime.strptime("12:00 PM", "%I:%M %p").time()
        return datetime.datetime.strptime(time_str, "%I:%M %p").time()

    def autopilot_scheduler():
        nonlocal last_checked_minute

        while True:
            if autopilot_mode:

                now = datetime.datetime.now()
                current_minute = now.strftime("%Y-%m-%d %H:%M")

                if current_minute != last_checked_minute:
                    last_checked_minute = current_minute

                    today = now.date()

                    for show, times in show_times.items():
                        for time_slot in times:

                            show_time = parse_show_time(time_slot)
                            show_dt = datetime.datetime.combine(today, show_time)

                            triggers = []

                            if "Ticket" in show:
                                triggers = [
                                    ("15", show_dt - datetime.timedelta(minutes=15)),
                                    ("10", show_dt - datetime.timedelta(minutes=10))
                                ]
                            else:
                                triggers = [
                                    ("5", show_dt - datetime.timedelta(minutes=5))
                                ]

                            for tag, t in triggers:
                                if t.strftime("%Y-%m-%d %H:%M") == current_minute:

                                    file_name = f"{show}_{time_slot.replace(':','')}.mp3"
                                    key = (file_name, tag)

                                    if key not in session_triggered_events:
                                        session_triggered_events.add(key)

                                        if os.path.exists(file_name):
                                            audio_queue.append(file_name)
                                            safe_ui(update_queue_display)

            time.sleep(1)

    threading.Thread(target=autopilot_scheduler, daemon=True).start()

    def toggle_autopilot():
        nonlocal autopilot_mode, session_triggered_events

        autopilot_mode = not autopilot_mode
        session_triggered_events.clear()

        if autopilot_mode:
            autopilot_btn.configure(text="AUTOPILOT: ON", fg_color="green")
        else:
            autopilot_btn.configure(text="AUTOPILOT: OFF", fg_color="red")

    # =====================================================
    # CONTROLS
    # =====================================================

    def enqueue_audio(show, time_slot):
        file_name = f"{show}_{time_slot.replace(':','')}.mp3"

        if not os.path.exists(file_name):
            return

        if file_name == current_playing_file:
            return

        if file_name in audio_queue:
            audio_queue.remove(file_name)
        else:
            audio_queue.append(file_name)

        update_queue_display()

    def stop_audio():
        nonlocal is_playing, current_playing_file
        pygame.mixer.music.stop()
        audio_queue.clear()
        is_playing = False
        current_playing_file = None
        update_queue_display()
        current_playing_var.set("Stopped")

    def toggle_theme():
        nonlocal theme_mode
        if theme_mode == "dark":
            ctk.set_appearance_mode("light")
            theme_btn.configure(text="LIGHT MODE")
            theme_mode = "light"
        else:
            ctk.set_appearance_mode("dark")
            theme_btn.configure(text="DARK MODE")
            theme_mode = "dark"

    # =====================================================
    # UI
    # =====================================================

    top_frame = ctk.CTkFrame(app)
    top_frame.pack(fill="x", pady=10, padx=20)

    ctk.CTkLabel(
        top_frame,
        text="Digha Science Centre – Announcement Control Panel",
        font=("Arial", 26, "bold")
    ).pack(side="left", padx=20)

    ctk.CTkLabel(
        top_frame,
        textvariable=clock_var,
        font=("Arial", 24)
    ).pack(side="right", padx=20)

    fullscreen_btn = ctk.CTkButton(
        top_frame,
        text="Exit Full Screen",
        fg_color="red",
        width=180,
        height=45,
        command=toggle_fullscreen
    )
    fullscreen_btn.pack(side="right", padx=10)

    theme_btn = ctk.CTkButton(
        top_frame, text="DARK MODE",
        width=180, height=45,
        command=toggle_theme
    )
    theme_btn.pack(side="right", padx=10)

    autopilot_btn = ctk.CTkButton(
        top_frame, text="AUTOPILOT: OFF",
        fg_color="red", width=180, height=45,
        command=toggle_autopilot
    )
    autopilot_btn.pack(side="right", padx=10)

    # =====================================================
    # SHOW UI (UNCHANGED)
    # =====================================================

    show_times = {
        "Space & Astronomy Call For Ticket": ["09:30 AM","10:30 AM","11:30 AM","12:00 NOON","12:30 PM","02:00 PM","03:00 PM","04:00 PM","04:30 PM","05:00 PM","05:30 PM","06:00 PM","06:30 PM","07:00 PM"],
        "Space & Astronomy Call For Show": ["09:30 AM","10:30 AM","11:30 AM","12:00 NOON","12:30 PM","02:00 PM","03:00 PM","04:00 PM","04:30 PM","05:00 PM","05:30 PM","06:00 PM","06:30 PM","07:00 PM"],
        "3D Show Call For Ticket": ["09:00 AM","10:00 AM","11:00 AM","12:00 NOON","12:30 PM","02:00 PM","03:30 PM","04:00 PM","04:30 PM","05:00 PM","05:30 PM","06:00 PM","06:30 PM","07:00 PM"],
        "3D Show Call For Show": ["09:00 AM","10:00 AM","11:00 AM","12:00 NOON","12:30 PM","02:00 PM","03:30 PM","04:00 PM","04:30 PM","05:00 PM","05:30 PM","06:00 PM","06:30 PM","07:00 PM"],
        "Fun Science Show Call For Ticket": ["12:00 NOON","01:00 PM","03:00 PM","04:00 PM","05:00 PM","06:00 PM","07:00 PM"],
        "Fun Science Show Call For Show": ["12:00 NOON","01:00 PM","03:00 PM","04:00 PM","05:00 PM","06:00 PM","07:00 PM"],
    }

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

            file_name = f"{show}_{time_slot.replace(':','')}.mp3"

            btn = ctk.CTkButton(
                button_frame,
                text=time_slot,
                height=55,
                fg_color=NORMAL_COLOR,
                command=lambda s=show, t=time_slot: enqueue_audio(s, t)
            )
            btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

            buttons_map[file_name] = btn

    for i, section in enumerate(ticket_sections):
        create_section(0, i, section)

    for i, section in enumerate(show_sections):
        create_section(1, i, section)

    # =====================================================
    # STATUS BAR
    # =====================================================

    bottom_frame = ctk.CTkFrame(app)
    bottom_frame.pack(fill="x", padx=20, pady=20)

    ctk.CTkLabel(bottom_frame, textvariable=current_playing_var, font=("Arial", 16)).pack(side="left", padx=20)
    ctk.CTkLabel(bottom_frame, textvariable=queue_status_var, font=("Arial", 16)).pack(side="left", padx=20)

    progress_bar = ctk.CTkProgressBar(bottom_frame, variable=progress_var, width=300)
    progress_bar.pack(side="left", padx=20)

    ctk.CTkLabel(bottom_frame, textvariable=progress_text_var, font=("Arial", 16)).pack(side="left")

    stop_btn = ctk.CTkButton(bottom_frame, text="STOP", fg_color="red", font=("Arial", 16), command=stop_audio)
    stop_btn.pack(side="right", padx=20)

    visualizer_frame = ctk.CTkFrame(bottom_frame)
    visualizer_frame.pack(side="right", padx=10)

    visualizer_segments = []
    for _ in range(20):
        bar = ctk.CTkFrame(visualizer_frame, width=10, height=30, fg_color=INACTIVE)
        bar.pack(side="left", padx=2)
        visualizer_segments.append(bar)

    def update_progress():
        if is_playing and current_length > 0:

            pos = pygame.mixer.music.get_pos() / 1000
            progress = min(pos / current_length, 1)
            progress_var.set(progress)

            elapsed = int(pos)
            total = current_length

            elapsed_str = f"{elapsed//60:02}:{elapsed%60:02}"
            total_str = f"{total//60:02}:{total%60:02}"

            progress_text_var.set(f"{elapsed_str} / {total_str}")

        else:
            progress_var.set(0)
            progress_text_var.set("00:00 / 00:00")

        app.after(200, update_progress)

    def update_visualizer():
        nonlocal fake_level
        fake_level = random.randint(5, 20) if is_playing else int(fake_level * 0.7)

        for i, bar in enumerate(visualizer_segments):
            if i < fake_level:
                bar.configure(fg_color=GREEN if i < 12 else YELLOW if i < 17 else RED)
            else:
                bar.configure(fg_color=INACTIVE)

        app.after(80, update_visualizer)

    update_progress()
    update_visualizer()

    app.update()

    app.mainloop()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    start_login()