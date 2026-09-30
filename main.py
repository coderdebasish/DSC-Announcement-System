import customtkinter as ctk
import pygame
import threading
import datetime
import time
import os
import random
from tkinter import filedialog, messagebox
from mutagen.mp3 import MP3

import database

# =========================================================
# PATH CONFIGURATION
# =========================================================

BASE_DIR = database.BASE_DIR
AUDIO_DIR = database.AUDIO_DIR
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# =========================================================
# LOGIN SYSTEM
# =========================================================

CORRECT_CODE = "721463"  # Postal Code of Digha Science Centre

def start_login():
    ctk.deactivate_automatic_dpi_awareness()

    login_app = ctk.CTk()

    # Window Icon
    icon_path = os.path.join(ASSETS_DIR, "logo.ico")
    if os.path.exists(icon_path):
        try:
            login_app.iconbitmap(icon_path)
        except Exception:
            pass

    # Center the window on screen
    screen_width = login_app.winfo_screenwidth()
    screen_height = login_app.winfo_screenheight()
    window_width = 600
    window_height = 700
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    login_app.geometry(f"{window_width}x{window_height}+{x}+{y}")
    login_app.focus_force()

    login_app.title("Digha Science Centre – Login")
    login_app.protocol("WM_DELETE_WINDOW", lambda: exit())

    ctk.CTkLabel(
        login_app,
        text="Digha Science Centre – Announcement System",
        font=("Arial", 20, "bold")
    ).pack(pady=20)

    ctk.CTkLabel(
        login_app,
        text="Enter 6 Digit Code",
        font=("Arial", 18)
    ).pack(pady=20)

    code_entry = ctk.CTkEntry(
        login_app,
        width=200, height=40, show="*", justify="center"
    )
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
            # Clear login widgets and transition to main dashboard
            for widget in login_app.winfo_children():
                widget.destroy()
            login_app.title("Digha Science Centre – Announcement System")
            open_main_app(login_app)
        else:
            error_label.configure(text="Incorrect Code ❌")
            code_entry.delete(0, 'end')

    login_app.bind("<Return>", lambda e: check_code())

    ctk.CTkButton(
        login_app,
        text="Login",
        width=180,
        height=45,
        fg_color="green",
        hover_color="#006400",
        command=check_code
    ).pack(pady=20)

    # Numeric On-Screen Touch Keyboard
    keyboard_frame = ctk.CTkFrame(login_app)
    keyboard_frame.pack(pady=5, padx=20)

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
                code_entry.delete(len(current) - 1, 'end')
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
# MAIN DASHBOARD
# =========================================================

def open_main_app(app):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Set Window Icon
    icon_path = os.path.join(ASSETS_DIR, "logo.ico")
    if os.path.exists(icon_path):
        try:
            app.iconbitmap(icon_path)
        except Exception:
            pass

    pygame.mixer.init()

    # Fullscreen State
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
            app.geometry("1280x820")
            fullscreen_btn.configure(text="Enter Full Screen", fg_color="green")
            is_fullscreen = False
        else:
            app.overrideredirect(True)
            app.geometry(f"{w}x{h}+0+0")
            fullscreen_btn.configure(text="Exit Full Screen", fg_color="red")
            is_fullscreen = True

    app.bind("<Escape>", lambda e: toggle_fullscreen())

    # =====================================================
    # STATE MANAGEMENT
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
    MISSING_COLOR = "#37474F"

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
    # SAFE UI THREADING
    # =====================================================

    def safe_ui(func, *args):
        app.after(0, func, *args)

    # =====================================================
    # BUTTON STATES
    # =====================================================

    def update_button_states():
        for file_path, btn in buttons_map.items():
            if file_path == current_playing_file:
                continue
            elif file_path in audio_queue:
                btn.configure(fg_color=QUEUE_COLOR)
            else:
                exists = os.path.exists(file_path)
                btn.configure(fg_color=NORMAL_COLOR if exists else MISSING_COLOR)

    def blink_playing_button():
        nonlocal blink_state
        if current_playing_file and current_playing_file in buttons_map:
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
                safe_ui(current_playing_var.set, f"Playing: {os.path.basename(file_path)}")

                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy() and is_playing:
                    time.sleep(0.1)

            except Exception as e:
                print(f"Audio playback error for {file_path}: {e}")
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
    # AUTOPILOT SCHEDULER (Dynamic from SQLite DB)
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

                    # Fetch live schedule dynamically from database
                    live_schedule = database.get_show_times()

                    for show, times in live_schedule.items():
                        for time_slot in times:
                            try:
                                show_time = parse_show_time(time_slot)
                                show_dt = datetime.datetime.combine(today, show_time)

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
                                        file_path = database.get_audio_path(show, time_slot)
                                        key = (file_path, tag)

                                        if key not in session_triggered_events:
                                            session_triggered_events.add(key)
                                            if os.path.exists(file_path):
                                                audio_queue.append(file_path)
                                                safe_ui(update_queue_display)
                            except Exception as ex:
                                print(f"Autopilot parse error: {ex}")

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
    # PLAYBACK CONTROLS
    # =====================================================

    def enqueue_audio(show, time_slot):
        file_path = database.get_audio_path(show, time_slot)

        if not os.path.exists(file_path):
            current_playing_var.set(f"⚠️ Missing audio: {time_slot}")
            return

        if file_path == current_playing_file:
            return

        if file_path in audio_queue:
            audio_queue.remove(file_path)
        else:
            audio_queue.append(file_path)

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
    # POPUP DIALOG: TIME SLOT & AUDIO MANAGER
    # =====================================================

    preview_channel = None

    def open_slot_manager():
        """Opens modal dialog for adding/removing time slots and attaching audio files."""
        dialog = ctk.CTkToplevel(app)
        dialog.title("Manage Show Time Slots & Recordings")
        dialog.geometry("780x640")
        dialog.minsize(700, 560)
        dialog.transient(app)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        dx = (app.winfo_screenwidth() - 780) // 2
        dy = (app.winfo_screenheight() - 640) // 2
        dialog.geometry(f"780x640+{dx}+{dy}")

        if os.path.exists(icon_path):
            try:
                dialog.iconbitmap(icon_path)
            except Exception:
                pass

        header = ctk.CTkFrame(dialog, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header,
            text="⚙ Show Time Slot & Audio Manager",
            font=("Arial", 22, "bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Manage database time slots and assign audio files dynamically. Changes reflect in UI immediately.",
            font=("Arial", 12),
            text_color="gray"
        ).pack(anchor="w")

        tabview = ctk.CTkTabview(dialog)
        tabview.pack(expand=True, fill="both", padx=20, pady=10)

        tab_add = tabview.add("➕ Add New Time Slot")
        tab_manage = tabview.add("📋 View & Remove Slots")

        # =================================================
        # TAB 1: ADD NEW TIME SLOT
        # =================================================

        add_frame = ctk.CTkFrame(tab_add, fg_color="transparent")
        add_frame.pack(expand=True, fill="both", padx=15, pady=10)

        # 1. Show Selection
        ctk.CTkLabel(add_frame, text="1. Select Show Category:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(5, 3))
        show_dropdown = ctk.CTkOptionMenu(
            add_frame,
            values=database.SHOW_CATEGORIES,
            width=450,
            height=35
        )
        show_dropdown.pack(anchor="w", pady=(0, 15))

        # 2. Time Slot Selection
        ctk.CTkLabel(add_frame, text="2. Enter / Pick Time Slot:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(5, 3))

        time_picker_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        time_picker_frame.pack(anchor="w", pady=(0, 5))

        hour_menu = ctk.CTkOptionMenu(
            time_picker_frame,
            values=["09", "10", "11", "12", "01", "02", "03", "04", "05", "06", "07", "08"],
            width=90
        )
        hour_menu.set("02")
        hour_menu.pack(side="left", padx=(0, 5))

        ctk.CTkLabel(time_picker_frame, text=":", font=("Arial", 16, "bold")).pack(side="left", padx=2)

        min_menu = ctk.CTkOptionMenu(
            time_picker_frame,
            values=["00", "15", "30", "45"],
            width=90
        )
        min_menu.set("30")
        min_menu.pack(side="left", padx=5)

        period_menu = ctk.CTkOptionMenu(
            time_picker_frame,
            values=["PM", "AM", "NOON"],
            width=95
        )
        period_menu.set("PM")
        period_menu.pack(side="left", padx=5)

        time_input = ctk.CTkEntry(
            time_picker_frame,
            width=150,
            placeholder_text="e.g. 02:30 PM"
        )
        time_input.insert(0, "02:30 PM")
        time_input.pack(side="left", padx=(15, 5))

        def update_time_input(*args):
            h = hour_menu.get()
            m = min_menu.get()
            p = period_menu.get()
            if p == "NOON" or (h == "12" and m == "00" and p == "PM"):
                time_input.delete(0, 'end')
                time_input.insert(0, "12:00 NOON")
            else:
                time_input.delete(0, 'end')
                time_input.insert(0, f"{h}:{m} {p}")
            update_preview_label()

        hour_menu.configure(command=update_time_input)
        min_menu.configure(command=update_time_input)
        period_menu.configure(command=update_time_input)

        # 3. Audio File Picker
        ctk.CTkLabel(add_frame, text="3. Attach Recording (MP3 / WAV):", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 3))

        audio_picker_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        audio_picker_frame.pack(fill="x", pady=(0, 5))

        selected_audio_path = ctk.StringVar(value="")

        audio_path_entry = ctk.CTkEntry(
            audio_picker_frame,
            textvariable=selected_audio_path,
            placeholder_text="No file selected (Optional — can attach later)",
            width=380
        )
        audio_path_entry.pack(side="left", padx=(0, 10))

        def browse_audio():
            file_path = filedialog.askopenfilename(
                title="Select Audio Recording",
                filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.m4a"), ("All Files", "*.*")]
            )
            if file_path:
                selected_audio_path.set(file_path)

        ctk.CTkButton(
            audio_picker_frame,
            text="📁 Browse...",
            width=110,
            command=browse_audio
        ).pack(side="left", padx=5)

        def test_play_audio():
            src = selected_audio_path.get()
            if src and os.path.exists(src):
                try:
                    pygame.mixer.music.load(src)
                    pygame.mixer.music.play()
                except Exception as e:
                    messagebox.showerror("Audio Error", f"Cannot play file: {e}")
            else:
                messagebox.showwarning("No File", "Please select a valid audio file to test play.")

        def test_stop_audio():
            pygame.mixer.music.stop()

        ctk.CTkButton(
            audio_picker_frame,
            text="▶ Test",
            width=70,
            fg_color="#00897B",
            hover_color="#00695C",
            command=test_play_audio
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            audio_picker_frame,
            text="⏹ Stop",
            width=70,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            command=test_stop_audio
        ).pack(side="left", padx=3)

        # 4. Formatted File Destination Info
        preview_dest_label = ctk.CTkLabel(
            add_frame,
            text="",
            font=("Arial", 11, "italic"),
            text_color="#90CAF9"
        )
        preview_dest_label.pack(anchor="w", pady=(5, 10))

        def update_preview_label(*args):
            s = show_dropdown.get()
            t = time_input.get().strip().upper()
            fname = database.format_audio_filename(s, t)
            preview_dest_label.configure(text=f"Destination in storage: audio/{fname}")

        show_dropdown.configure(command=lambda _: update_preview_label())
        update_preview_label()

        status_msg = ctk.CTkLabel(add_frame, text="", font=("Arial", 13, "bold"))
        status_msg.pack(pady=5)

        # 5. Save Button
        def save_new_slot():
            show = show_dropdown.get()
            raw_time = time_input.get().strip().upper()
            audio_src = selected_audio_path.get().strip() or None

            success, msg = database.add_time_slot(show, raw_time, audio_src)
            if success:
                status_msg.configure(text=f"✅ {msg}", text_color="green")
                render_all_sections()
                populate_manage_list()
                selected_audio_path.set("")
            else:
                status_msg.configure(text=f"❌ {msg}", text_color="red")

        ctk.CTkButton(
            add_frame,
            text="💾 Save & Add Time Slot to Dashboard",
            height=45,
            font=("Arial", 15, "bold"),
            fg_color="green",
            hover_color="#006400",
            command=save_new_slot
        ).pack(fill="x", pady=10)

        # =================================================
        # TAB 2: MANAGE & REMOVE TIME SLOTS
        # =================================================

        manage_frame = ctk.CTkFrame(tab_manage, fg_color="transparent")
        manage_frame.pack(expand=True, fill="both", padx=15, pady=10)

        # Filter row
        filter_row = ctk.CTkFrame(manage_frame, fg_color="transparent")
        filter_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(filter_row, text="Select Show:", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 10))

        manage_show_dropdown = ctk.CTkOptionMenu(
            filter_row,
            values=database.SHOW_CATEGORIES,
            width=380,
            command=lambda _: populate_manage_list()
        )
        manage_show_dropdown.pack(side="left")

        stats_label = ctk.CTkLabel(filter_row, text="", font=("Arial", 12), text_color="gray")
        stats_label.pack(side="right", padx=10)

        # Scrollable list for slots
        slots_list_frame = ctk.CTkScrollableFrame(manage_frame, height=360)
        slots_list_frame.pack(expand=True, fill="both")

        delete_file_checkbox_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            manage_frame,
            text="Also permanently delete associated MP3 file from audio/ when deleting a slot",
            variable=delete_file_checkbox_var
        ).pack(anchor="w", pady=(10, 0))

        def populate_manage_list():
            for w in slots_list_frame.winfo_children():
                w.destroy()

            selected_show = manage_show_dropdown.get()
            all_shows = database.get_show_times()
            show_slots = all_shows.get(selected_show, [])

            total = len(show_slots)
            with_audio = sum(1 for s in show_slots if database.check_audio_status(selected_show, s))
            stats_label.configure(text=f"Total: {total} slots | Audio Available: {with_audio}/{total}")

            if not show_slots:
                ctk.CTkLabel(
                    slots_list_frame,
                    text="No time slots found for this show. Add one in the 'Add New' tab.",
                    font=("Arial", 14),
                    text_color="gray"
                ).pack(pady=40)
                return

            for slot in show_slots:
                row_card = ctk.CTkFrame(slots_list_frame, corner_radius=8)
                row_card.pack(fill="x", pady=4, padx=5)

                time_badge = ctk.CTkLabel(
                    row_card,
                    text=slot,
                    font=("Arial", 14, "bold"),
                    width=110,
                    anchor="w"
                )
                time_badge.pack(side="left", padx=12, pady=8)

                has_audio = database.check_audio_status(selected_show, slot)
                expected_filename = database.format_audio_filename(selected_show, slot)

                status_label = ctk.CTkLabel(
                    row_card,
                    text=f"🟢 {expected_filename}" if has_audio else f"⚠️ Missing audio ({expected_filename})",
                    font=("Arial", 12),
                    text_color="#81C784" if has_audio else "#FFB74D",
                    anchor="w"
                )
                status_label.pack(side="left", expand=True, fill="x", padx=10)

                # Play button if audio exists
                if has_audio:
                    audio_full_path = database.get_audio_path(selected_show, slot)
                    play_btn = ctk.CTkButton(
                        row_card,
                        text="▶",
                        width=35,
                        height=30,
                        fg_color="#00897B",
                        hover_color="#00695C",
                        command=lambda p=audio_full_path: play_preview(p)
                    )
                    play_btn.pack(side="left", padx=4)

                # Attach/Replace Audio button
                attach_btn = ctk.CTkButton(
                    row_card,
                    text="📁 Replace",
                    width=80,
                    height=30,
                    fg_color="#1E88E5",
                    hover_color="#1565C0",
                    command=lambda s=selected_show, sl=slot: replace_audio_dialog(s, sl)
                )
                attach_btn.pack(side="left", padx=4)

                # Delete Button
                del_btn = ctk.CTkButton(
                    row_card,
                    text="🗑 Delete",
                    width=75,
                    height=30,
                    fg_color="#E53935",
                    hover_color="#C62828",
                    command=lambda s=selected_show, sl=slot: confirm_delete_slot(s, sl)
                )
                del_btn.pack(side="right", padx=8)

        def play_preview(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
            except Exception as e:
                messagebox.showerror("Error", f"Playback failed: {e}")

        def replace_audio_dialog(show, slot):
            new_file = filedialog.askopenfilename(
                title=f"Select New Audio for {show} ({slot})",
                filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.m4a"), ("All Files", "*.*")]
            )
            if new_file:
                ok, msg = database.add_time_slot(show, slot, new_file)
                if ok:
                    populate_manage_list()
                    render_all_sections()
                    messagebox.showinfo("Success", f"Audio updated for {slot}!")
                else:
                    messagebox.showerror("Error", msg)

        def confirm_delete_slot(show, slot):
            should_delete_file = delete_file_checkbox_var.get()
            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete time slot '{slot}' from '{show}'?"
                + ("\n\nThe MP3 audio file will also be deleted from disk!" if should_delete_file else "")
            )
            if confirm:
                ok, msg = database.delete_time_slot(show, slot, delete_file=should_delete_file)
                if ok:
                    populate_manage_list()
                    render_all_sections()
                else:
                    messagebox.showerror("Error", msg)

        populate_manage_list()

    # =====================================================
    # HEADER UI
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
        width=160,
        height=45,
        command=toggle_fullscreen
    )
    fullscreen_btn.pack(side="right", padx=8)

    theme_btn = ctk.CTkButton(
        top_frame, text="DARK MODE",
        width=150, height=45,
        command=toggle_theme
    )
    theme_btn.pack(side="right", padx=8)

    autopilot_btn = ctk.CTkButton(
        top_frame, text="AUTOPILOT: OFF",
        fg_color="red", width=160, height=45,
        command=toggle_autopilot
    )
    autopilot_btn.pack(side="right", padx=8)

    # Manage Slots Button
    manage_slots_btn = ctk.CTkButton(
        top_frame,
        text="⚙ MANAGE SLOTS",
        fg_color="#D84315",
        hover_color="#BF360C",
        font=("Arial", 14, "bold"),
        width=170,
        height=45,
        command=open_slot_manager
    )
    manage_slots_btn.pack(side="right", padx=8)

    # =====================================================
    # DYNAMIC SHOW GRID UI
    # =====================================================

    main_frame = ctk.CTkFrame(app)
    main_frame.pack(expand=True, fill="both", padx=20, pady=10)

    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)

    for i in range(3):
        main_frame.grid_columnconfigure(i, weight=1)

    def create_section(row, col, show, times):
        """Creates a show section with scrollable button grid for unlimited slots."""
        frame = ctk.CTkFrame(main_frame, corner_radius=15)
        frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

        header_box = ctk.CTkFrame(frame, fg_color="transparent")
        header_box.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkLabel(
            header_box,
            text=show,
            font=("Arial", 16, "bold")
        ).pack(side="left")

        ctk.CTkLabel(
            header_box,
            text=f"({len(times)} slots)",
            font=("Arial", 12),
            text_color="gray"
        ).pack(side="right")

        # Scrollable frame allows unlimited time slots to be added
        button_scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        button_scroll.pack(expand=True, fill="both", padx=6, pady=6)

        for i in range(4):
            button_scroll.grid_columnconfigure(i, weight=1)

        for i, time_slot in enumerate(times):
            r = i // 4
            c = i % 4

            file_path = database.get_audio_path(show, time_slot)
            has_file = os.path.exists(file_path)

            btn = ctk.CTkButton(
                button_scroll,
                text=time_slot if has_file else f"{time_slot} ⚠️",
                height=48,
                font=("Arial", 13, "bold"),
                fg_color=NORMAL_COLOR if has_file else MISSING_COLOR,
                hover_color="#1565C0" if has_file else "#455A64",
                command=lambda s=show, t=time_slot: enqueue_audio(s, t)
            )
            btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
            buttons_map[file_path] = btn

    def render_all_sections():
        """Fetches live schedule from SQLite database and renders all 6 sections."""
        for widget in main_frame.winfo_children():
            widget.destroy()

        buttons_map.clear()
        live_shows = database.get_show_times()

        ticket_sections = [k for k in database.SHOW_CATEGORIES if "Ticket" in k]
        show_sections = [k for k in database.SHOW_CATEGORIES if "Show" in k and "Ticket" not in k]

        for i, section in enumerate(ticket_sections):
            create_section(0, i, section, live_shows.get(section, []))

        for i, section in enumerate(show_sections):
            create_section(1, i, section, live_shows.get(section, []))

        update_queue_display()

    # Initial render of all sections
    render_all_sections()

    # =====================================================
    # STATUS BAR & VISUALIZER
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
            if pos < 0:
                pos = 0
            progress = min(pos / current_length, 1.0)
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
# APPLICATION ENTRYPOINT
# =========================================================

if __name__ == "__main__":
    start_login()
