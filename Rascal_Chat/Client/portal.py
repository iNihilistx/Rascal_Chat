import subprocess
import signal
import sys
import os

import customtkinter
from cryptography.fernet import Fernet
from PIL import Image


class EntryForm(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        customtkinter.set_default_color_theme("blue")
        customtkinter.set_appearance_mode("dark")

        self.protocol("WM_DELETE_WINDOW", self.on_exit)  # uses built-in window manager to detect a close event then call the closing function
        signal.signal(signal.SIGINT, self.on_exit)  # from the signal lib - signal.SIGINT is when an interrupt is detected, so either ctrl + c or closing button
        # signal.signal(signal.SIGCHLD, self.on_exit) #sigchild is sent to the parent process when a child process terminates, specifies that the on_exit should get called

        self.geometry("680x400")
        self.title("Rascal Chat: Client Portal")
        self.resizable(False, False)

        IMAGE_PATH = 'RLogo.jpg'
        IMAGE_WIDTH = 400
        IMAGE_HEIGHT = 400

        self.image = customtkinter.CTkImage(dark_image=Image.open(os.path.join(IMAGE_PATH)), size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        self.label = customtkinter.CTkLabel(self, image=self.image, text='')
        self.label.grid(row=0, column=0)

        self.logo_frame = customtkinter.CTkFrame(self, fg_color="#F5F5F5", height=20, corner_radius=10, border_width=4, border_color="#0963a7")
        self.logo_frame.grid(row=0, column=1, padx=25, pady=55)

        self.title = customtkinter.CTkLabel(self.logo_frame, text="Rascal Chat: Client Portal", font=("", 16, "bold"), text_color="#2C3E50")
        self.title.grid(row=0, column=0, sticky="nsew", pady=5, padx=10)

        self.sep_line = customtkinter.CTkFrame(self.logo_frame, bg_color="#353535", height=1)
        self.sep_line.grid(row=1, column=0, sticky="nsew", pady=20, padx=10)

        self.server_ip_address = customtkinter.CTkEntry(self.logo_frame, placeholder_text="Server IP Address...", font=("", 13), placeholder_text_color="black", text_color="black", fg_color="#f3f1f0", height=30, corner_radius=7)
        self.server_ip_address.grid(row=2, column=0, sticky="nsew", padx=30)

        self.server_port = customtkinter.CTkEntry(self.logo_frame, placeholder_text="Server Port...", font=("", 13), placeholder_text_color="black", text_color="black", fg_color="#f3f1f0", height=30, corner_radius=7)
        self.server_port.grid(row=3, column=0, sticky="nsew", padx=30, pady=20)

        self.username = customtkinter.CTkEntry(self.logo_frame, placeholder_text="Username...", font=("", 13), placeholder_text_color="black", text_color="black", fg_color="#f3f1f0", height=30, corner_radius=7)
        self.username.grid(row=4, column=0, sticky="nsew", padx=30, pady=1)

        self.loginButton = customtkinter.CTkButton(self.logo_frame, text="Login", height=40, width=150, font=("", 13, "bold"), corner_radius=9, fg_color="#003a86", hover_color="#000099", command=self.connect_window)
        self.loginButton.grid(row=5, column=0, sticky="nsew", pady=20, padx=35)

        self.clientWindow = None

    def load_key(self):
        file = open("key.key", "rb")
        key = file.read()
        file.close()
        return key

    def encrypt_server_details(self, server_ip, server_port, username):
        key = self.load_key()
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(f"{server_ip}|{server_port}|{username}".encode())

        with open("server.txt", "wb") as server_details:
            server_details.write(encrypted_data)

    def connect_window(self):
        self.server_ip = self.server_ip_address.get()
        self.server_port = int(self.server_port.get())
        self.my_username = self.username.get()

        self.encrypt_server_details(self.server_ip, self.server_port, self.my_username)

        if self.clientWindow is None or not self.clientWindow.winfo_exists():
            python_command = sys.executable
            self.destroy()
            self.run = subprocess.Popen([python_command, 'chat_client.py'])

    def on_exit(self):
        self.destroy()  # destroy the window

if __name__ == "__main__":

    """
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)
    """

    app = EntryForm()
    app.mainloop()
