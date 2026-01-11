import tkinter as tk
from tkinter import *
from tkinter import messagebox
import pygame

# Initialize pygame mixer
pygame.mixer.init()

# Function to play the selected MP3 file
def play_mp3(show, time_slot):
    time_slot_new = time_slot[:2] + time_slot[3:]
    file_name = f"{show}_{time_slot_new}.mp3"
    print(file_name)
    try:
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()
        messagebox.showinfo("Playing", f"Now playing: {file_name}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not play {file_name}: {e}")
def stop_music():
    pygame.mixer.music.stop()
    messagebox.showinfo("Music Stop", f"Announcement Stopped")
      

def select_show(show):
    def submit_time():
        time_slot = selected_time.get()
        if time_slot:
            play_mp3(show, time_slot)
        else:
            messagebox.showwarning("Warning", "Please select a time slot.")
    
    time_window = tk.Toplevel()
    time_window.title(f"{show}")
    time_window.minsize(400,300)
    selected_time = tk.StringVar()
    
    time_slots = show_times[show]
    for time_slot in time_slots:
    #for index in range(len(time_slot)):    
        btn = tk.Radiobutton(time_window, text=time_slot, variable=selected_time, 
        value=time_slot, font =("Impact",14),
        indicatoron=0) #indicator to remove round click circle and use whole text as button
        btn.pack(padx=10, pady=5)
    
    submit_btn = tk.Button(time_window, text="Submit",font =("Impact",14), command=submit_time) #button to submit time
    submit_btn.pack(pady=10)

root = tk.Tk()
root.title("Digha Science Centre Show Announcement")
#root.minsize(400, 200)
root.geometry("620x650")
icon = PhotoImage(file = 'logo.png')
root.iconphoto(True, icon)
root.config(background="#d9dee6")
#bgimg= tk.PhotoImage(file = "")
#limg= Label(root, i=bgimg)
#limg.pack()
label = Label(root, text="Select Shows", font=('Arial',15,'bold'),) #main window, text, font, background, relief = border
label.pack()
root.update_idletasks()
window_width = root.winfo_width()
window_height = root.winfo_height()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height/2 - window_height/2)
position_right = int(screen_width/2 - window_width/2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
stop_btn = tk.Button(root,  text="STOP!", font=('Arial',25,'bold',), command=stop_music)
stop_btn.place(x=241,y = 570)


show_times = {
    "Space & Astronomy Call For Show": ["09:30 AM", "10:30 AM", "11:30 AM", "12:00 NOON", "12:30 PM", "02:00 PM", "03:00 PM", "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM"],
    "Space & Astronomy Call For Ticket": ["09:30 AM", "10:30 AM", "11:30 AM", "12:00 NOON", "12:30 PM", "02:00 PM", "03:00 PM", "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM"],
    "3D Show Call For Show": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 NOON", "12:30 PM", "02:00 PM", "03:30 PM", "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM"],
    "3D Show Call For Ticket": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 NOON", "12:30 PM", "02:00 PM", "03:30 PM", "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM"],
    "Fun Science Show Call For Show": ["12:00 NOON", "01:00 PM", "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM","07:00 PM"],
    "Fun Science Show Call For Ticket": ["12:00 NOON", "01:00 PM", "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM","07:00 PM"],
    "Taramandal Show Call for Show": ["10:30 AM", "11:30 PM", "12:30 PM","01:30 PM","02:30 PM","03:30 PM","04:30 PM","05:30 PM","06:30 PM"],
    "Taramandal Show Call for Ticket": ["10:30 AM", "11:30 PM", "12:30 PM","01:30 PM","02:30 PM","03:30 PM","04:30 PM","05:30 PM","06:30 PM"]
}

for show in show_times.keys():
    btn = tk.Button(root, text=show, font=('Arial',15,'bold'),command=lambda s=show: select_show(s))
    btn.pack(padx=10, pady=12)


root.mainloop()
