import tkinter as tk
from tkinter import messagebox
import pygame

pygame.mixer.init()

def play_mp3(show, time_slot):
    time_slot_new = time_slot[:2] + time_slot[3:]
    file_name = f"{show}_{time_slot_new}.mp3"
    try:
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()
    except Exception as e:
        messagebox.showerror("Error", f"Cannot play:\n{file_name}")

def stop_music():
    pygame.mixer.music.stop()

root = tk.Tk()
root.title("Digha Science Centre – Show Announcements")
root.geometry("1400x850")
root.configure(bg="#d9dee6")

title = tk.Label(
    root,
    text="Digha Science Centre – Show Announcements",
    font=("Arial", 24, "bold"),
    bg="#d9dee6"
)
title.pack(pady=10)

canvas = tk.Canvas(root, bg="#d9dee6")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg="#d9dee6")

scroll_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

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

row = 0
for show, times in show_times.items():
    show_label = tk.Label(
        scroll_frame,
        text=show,
        font=("Arial", 18, "bold"),
        bg="#c5f63e"
    )
    show_label.grid(row=row, column=0, sticky="w", pady=(20, 5))
    row += 1

    col = 0
    for time in times:
        btn = tk.Button(
            scroll_frame,
            text=time,
            font=("Arial", 14, "bold"),
            width=10,
            height=2,
            command=lambda s=show, t=time: play_mp3(s, t)
        )
        btn.grid(row=row, column=col, padx=5, pady=5)
        col += 1
        if col > 6:
            col = 0
            row += 1

    row += 1

stop_btn = tk.Button(
    root,
    text="STOP",
    font=("Arial", 28, "bold"),
    bg="red",
    fg="white",
    command=stop_music
)
stop_btn.pack(pady=10)

root.mainloop()
