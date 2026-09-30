"""
Database & Schedule Management Module
Digha Science Centre – Announcement System

Handles local SQLite storage for show time slots, audio file associations,
and dynamic scheduling without code modification.
"""

import os
import sqlite3
import shutil
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
DB_PATH = os.path.join(BASE_DIR, "schedule.db")

# Fixed core show categories (2 rows x 3 columns layout)
SHOW_CATEGORIES = [
    "Space & Astronomy Call For Ticket",
    "Space & Astronomy Call For Show",
    "3D Show Call For Ticket",
    "3D Show Call For Show",
    "Fun Science Show Call For Ticket",
    "Fun Science Show Call For Show",
]

# Default baseline schedule (used to seed empty database)
DEFAULT_SHOW_TIMES = {
    "Space & Astronomy Call For Ticket": [
        "09:30 AM", "10:30 AM", "11:30 AM", "12:00 NOON", "12:30 PM",
        "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
        "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM"
    ],
    "Space & Astronomy Call For Show": [
        "09:30 AM", "10:30 AM", "11:30 AM", "12:00 NOON", "12:30 PM",
        "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
        "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM"
    ],
    "3D Show Call For Ticket": [
        "09:00 AM", "10:00 AM", "11:00 AM", "12:00 NOON", "12:30 PM",
        "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
        "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM"
    ],
    "3D Show Call For Show": [
        "09:00 AM", "10:00 AM", "11:00 AM", "12:00 NOON", "12:30 PM",
        "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
        "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM"
    ],
    "Fun Science Show Call For Ticket": [
        "10:00 AM", "11:00 AM", "12:00 NOON", "01:00 PM", "02:00 PM",
        "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM"
    ],
    "Fun Science Show Call For Show": [
        "10:00 AM", "11:00 AM", "12:00 NOON", "01:00 PM", "02:00 PM",
        "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM"
    ],
}


def time_sort_key(time_str: str) -> datetime.time:
    """Helper for chronologically sorting time strings (e.g. 09:30 AM before 12:00 NOON)."""
    try:
        clean = time_str.strip().upper()
        if "NOON" in clean:
            return datetime.time(12, 0)
        return datetime.datetime.strptime(clean, "%I:%M %p").time()
    except Exception:
        return datetime.time(23, 59)


def format_audio_filename(show_name: str, time_slot: str) -> str:
    """Generates standard standardized audio filename: e.g. '3D Show Call For Show_0200 PM.mp3'."""
    clean_time = time_slot.replace(":", "").strip()
    return f"{show_name}_{clean_time}.mp3"


def get_audio_path(show_name: str, time_slot: str) -> str:
    """
    Resolves the absolute path for a show's audio file.
    Searches in 'audio/' first, then falls back to project root.
    """
    filename = format_audio_filename(show_name, time_slot)
    in_audio_dir = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(in_audio_dir):
        return in_audio_dir
    in_root_dir = os.path.join(BASE_DIR, filename)
    if os.path.exists(in_root_dir):
        return in_root_dir
    return in_audio_dir


def init_db():
    """Initializes the SQLite database and seeds default time slots if empty."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            show_name TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            audio_file TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(show_name, time_slot)
        )
    """)
    conn.commit()

    # Check if empty
    cursor.execute("SELECT COUNT(*) FROM time_slots")
    count = cursor.fetchone()[0]

    if count == 0:
        print("[Database] Seeding initial show time slots...")
        for show, slots in DEFAULT_SHOW_TIMES.items():
            for slot in slots:
                audio_name = format_audio_filename(show, slot)
                cursor.execute("""
                    INSERT OR IGNORE INTO time_slots (show_name, time_slot, audio_file)
                    VALUES (?, ?, ?)
                """, (show, slot, audio_name))
        conn.commit()

    conn.close()


def get_show_times() -> dict[str, list[str]]:
    """Returns a dict mapping show_name -> list of chronologically sorted time slots."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    result = {cat: [] for cat in SHOW_CATEGORIES}

    cursor.execute("SELECT show_name, time_slot FROM time_slots")
    rows = cursor.fetchall()
    conn.close()

    for show_name, time_slot in rows:
        if show_name in result:
            result[show_name].append(time_slot)
        else:
            result.setdefault(show_name, []).append(time_slot)

    # Sort each show's time slots chronologically
    for show_name in result:
        result[show_name].sort(key=time_sort_key)

    return result


def add_time_slot(show_name: str, time_slot: str, source_audio_path: str = None) -> tuple[bool, str]:
    """
    Adds a new time slot to the database and optionally copies/renames the audio file.
    Returns (success: bool, message: str).
    """
    show_name = show_name.strip()
    time_slot = time_slot.strip().upper()

    if not show_name or not time_slot:
        return False, "Show name and time slot cannot be empty."

    # Validate time format
    try:
        if "NOON" not in time_slot:
            datetime.datetime.strptime(time_slot, "%I:%M %p")
    except ValueError:
        return False, f"Invalid time format: '{time_slot}'. Please use format like '02:30 PM' or '12:00 NOON'."

    os.makedirs(AUDIO_DIR, exist_ok=True)
    target_filename = format_audio_filename(show_name, time_slot)
    target_path = os.path.join(AUDIO_DIR, target_filename)

    # Copy audio file if provided
    if source_audio_path:
        if not os.path.exists(source_audio_path):
            return False, f"Source audio file not found: {source_audio_path}"
        try:
            # Only copy if source is different from target
            if os.path.abspath(source_audio_path) != os.path.abspath(target_path):
                shutil.copy2(source_audio_path, target_path)
        except Exception as e:
            return False, f"Failed to copy audio file: {e}"

    # Insert into database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO time_slots (show_name, time_slot, audio_file)
            VALUES (?, ?, ?)
            ON CONFLICT(show_name, time_slot) DO UPDATE SET audio_file=excluded.audio_file
        """, (show_name, time_slot, target_filename))
        conn.commit()
        conn.close()
        return True, f"Time slot '{time_slot}' successfully added to '{show_name}'."
    except Exception as e:
        return False, f"Database error: {e}"


def delete_time_slot(show_name: str, time_slot: str, delete_file: bool = False) -> tuple[bool, str]:
    """
    Deletes a time slot from the database, and optionally removes the MP3 file from audio/.
    Returns (success: bool, message: str).
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM time_slots WHERE show_name = ? AND time_slot = ?", (show_name, time_slot))
        conn.commit()
        conn.close()

        if delete_file:
            target_filename = format_audio_filename(show_name, time_slot)
            target_path = os.path.join(AUDIO_DIR, target_filename)
            if os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except Exception as e:
                    return True, f"Time slot removed, but could not delete file: {e}"

        return True, f"Time slot '{time_slot}' removed from '{show_name}'."
    except Exception as e:
        return False, f"Database error: {e}"


def check_audio_status(show_name: str, time_slot: str) -> bool:
    """Returns True if the audio file for this slot exists on disk."""
    path = get_audio_path(show_name, time_slot)
    return os.path.exists(path)
