import socket
import customtkinter
import threading

class Server(customtkinter.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master, fg_color="#121412", border_color="#303030", border_width=2)

        self.master.protocol("WM_DELETE_WINDOW", self.on_exit)

        self.grid_columnconfigure(0, weight=1)

        self.title = title
        self.title_label = customtkinter.CTkLabel(self, text=self.title, fg_color="#2081E1", corner_radius=8)
        self.title_label.grid(row=0, column=0, padx=50, sticky="nsew", pady=(10, 0))

        self.clients = []
        self.current_users = 0

        self.chat_history = customtkinter.CTkTextbox(
            self,
            height=600,
            width=650,
            text_color="white",
            fg_color="#1F1F1F",
            border_color="gray30",
            border_width=1,
        )
        self.chat_history.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.user_count_label = customtkinter.CTkLabel(self, text="0/0 users connected")
        self.user_count_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))

        self.HOST = "192.168.0.26"
        self.PORT = 8080
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(10)

        self.chat_history.insert("end", "[SERVER] Server is listening...\n")
        threading.Thread(target=self.accept_connection).start()
    
    def set_max_users(self, max_users):
        self.max_users = max_users
        self.user_count_label.configure(text=f"{self.current_users}/{self.max_users} users connected")


    def accept_connection(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            if self.current_users < self.max_users:
                self.current_users += 1
                self.chat_history.insert("end", f"[CONNECTION ESTABLISHED] {client_address} has connected.\n")
                self.user_count_label.configure(text=f"{self.current_users}/{self.max_users} users connected")
                self.clients.append(client_socket)

            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
            
    def handle_client(self, client_socket, client_address):
        while True:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                if not message:
                    break

                for client in self.clients:
                    if client != client_socket:
                        client.sendall(message.encode("utf-8"))
                self.chat_history.insert("end", f"[{client_address}]: {message}\n")
                self.chat_history.update()
            except Exception as error:
                print("[ERROR]", str(error))
                break

        client_socket.close()
        self.clients.remove(client_socket)
        self.current_users -= 1
        self.user_count_label.configure(text=f"{self.current_users}/{self.max_users} users connected")

        user_disconnection = f"[DISCONNECTION] {client_address} has left Rascal Chat.\n"
        self.chat_history.insert("end", user_disconnection)
        for client in self.clients:
            client.sendall(user_disconnection.encode("utf-8"))
        self.chat_history.update()

    def on_exit(self):
        self.master.destroy()
        self.server_socket.close()
        self.destroy()

class BuildFrame(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        customtkinter.set_default_color_theme("green")
        self.hostname = socket.gethostname()
        self.ipaddr = socket.gethostbyname(self.hostname)

        self.title(f"Server Host: {self.ipaddr} {self.hostname}")
        self.geometry("700x800")
        self._set_appearance_mode("dark")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.ServerFrame = Server(self, "Rascal Chat")
        self.ServerFrame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

if __name__ == "__main__":
    app = BuildFrame()
    app.ServerFrame.set_max_users(10)  # Set the maximum number of users to 10
    app.mainloop()
