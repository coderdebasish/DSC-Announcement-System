import customtkinter as ctk
from tkinter import messagebox


CORRECT_CODE = "721463" #pin code of dsc digha

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


login_app = ctk.CTk()
login_app.geometry("600x400")
login_app.title("Digha Science Centre – Announcement System")
label = ctk.CTkLabel(login_app, text="Digha Science Centre – Announcement System Login Panel", font=("Arial", 20, "bold"))
label.pack(pady=15)
label = ctk.CTkLabel(login_app, text="Enter 6 Digit Code", font=("Arial", 20, "bold"))
label.pack(pady=30)

code_entry = ctk.CTkEntry(login_app, width=200, height=40, show="*",  justify="center",)
code_entry.pack(pady=10)
error_label = ctk.CTkLabel(login_app, text="", text_color="red")
error_label.pack(pady=5)


login_app.bind("<Return>", lambda e: check_code())
def check_code():
    entered = code_entry.get()

    if entered == CORRECT_CODE:
        login_app.destroy()   # to destroy the login window
             
    else:
        error_label.configure(text="Incorrect Code ❌")
        code_entry.delete(0, 'end')   # if code is bhul, then clear input



btn = ctk.CTkButton(login_app, text="Login",  width=180,
    height=45,fg_color="green",    
    hover_color="black",  
    text_color="white",  command=check_code)
btn.pack(pady=3)


login_app.mainloop()