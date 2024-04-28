import socket
import subprocess
import customtkinter
import os
import threading
from cryptography.fernet import Fernet
import sys
from tkinter import *

class ClientNetwork(customtkinter.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, fg_color="#121412", border_color="#303030", border_width=2)
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_exit)

        self.grid_columnconfigure(0, weight=1)

        self.title = title
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="#2081E1", corner_radius=8)
        self.title.grid(row=0, column=0, padx=50, sticky="nsew", pady=(10,0))

        self.message_receiver = customtkinter.CTkTextbox(self, width=800, height=400, text_color="white", fg_color="#1F1F1F", border_color="gray30", border_width=1)
        self.message_receiver.grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.message_sender = customtkinter.CTkEntry(
            self,
            width=800,
            height=60,
            text_color="white",
            fg_color="#1F1F1F",
            border_color="gray30",
            border_width=1,
            placeholder_text="Enter Message..."
        )
        self.message_sender.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.message_sender.bind("<Return>", lambda event: self.send_message())

        self.thread = None
        thread = threading.Thread(target=self.client_socket, daemon=True)
        thread.start()

    def load_key(self):
        file = open("key.key", "rb")
        key = file.read()
        file.close()
        return key
    
    def decrypt_server_details(self, encrypted_details):
        key = self.load_key()
        cipher = Fernet(key)
        decrypted_details = cipher.decrypt(encrypted_details).decode()
        return decrypted_details

    def get_server(self):
        with open("server.txt", "rb") as server_file:
            encrypted_data = server_file.read()
        
        decrypted_data = self.decrypt_server_details(encrypted_data)

        for line in decrypted_data.splitlines():
            data = line.rstrip()
            self.ip, self.port, self.username = data.split("|")
            print(self.ip, self.port, self.username)

    def client_socket(self):
        self.get_server()
        message = f"[?] Attempting to connect to: {self.ip}:{self.port}"
        self.message_receiver.insert("end", message + "\n")

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((self.ip, int(self.port)))
        except ConnectionRefusedError:
            self.message_receiver.insert("end", "[!] Connection refused by server\n")
            return

        self.message_receiver.insert("end", f"\n[+] Connected to: {self.ip}\n")
        self.message_receiver.yview(END)
        self.message_receiver.update()

        # Bind the send_message method to the Return key press event after connection is established
        self.message_sender.bind("<Return>", lambda event: self.send_message())

        receive_thread = threading.Thread(target=self.receive_message)
        receive_thread.daemon = True
        receive_thread.start()


    def send_message(self):
        message = self.message_sender.get()

        if message:
            try:
                full_message = f"{self.username}:{message}"
                self.client.sendall(full_message.encode('utf-8'))
                self.message_receiver.insert("end", f"{self.username}: {message}\n")
            except ConnectionResetError:
                self.message_receiver.insert("end", "[!]Connection closed by server\n")
                self.message_receiver.yview(END)
        self.message_sender.delete(0, 'end')

    def receive_message(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                self.message_receiver.insert("end", message + "\n")
                self.message_receiver.yview(END)
            except ConnectionRefusedError:
                self.message_receiver.insert("end", "[!]Connection closed by server...")
                self.message_receiver.yview(END)
                break


    def on_exit(self):
        self.master.destroy()

class ClientBuilder(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        customtkinter.set_default_color_theme("blue")
        customtkinter.set_appearance_mode("dark")
        
        self.geometry("860x600")
        self.resizable(False, False)

        self.title("Rascal Chat Client")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.clientNetwork = ClientNetwork(self, "Rascal Chat Client")
        self.clientNetwork.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

if __name__ == "__main__":
    app = ClientBuilder()
    app.mainloop()