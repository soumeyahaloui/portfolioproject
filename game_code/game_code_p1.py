import socket

import customtkinter as ctk

from tkinter import Label, ttk
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.simpledialog as simpledialog
import threading
import json


ctk.set_appearance_mode("Dark")

global room_window
room_window = None  # Initialize it as None
game_data_table = None

global player_one_pin_entries, player_two_pin_entries
player_one_pin_entries = []
player_two_pin_entries = []

global player_one_name, player_two_name
player_one_name = ""
player_two_name = ""

# Client configuration
host = '127.0.0.1'  # localhost
port = 65432

# Connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))


def listen_for_server_messages():
    global room_window, opponent_name, player_name, game_data_table
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            # Check if the message is JSON formatted
            if message.startswith('{') and message.endswith('}'):
                try:
                    data = json.loads(message)
                    # Print the received data (name and number)
                    print("Received opponent's data:", data)
                except json.JSONDecodeError:
                    print("Received non-JSON data:", message)

            elif message == "START_GAME":
                root.after(0, lambda: open_data_entry_window(
                    room_window) if room_window else None)

        except Exception as e:
            print(f"Error in listen_for_server_messages: {e}")
            break


# Start the listening thread
listening_thread = threading.Thread(target=listen_for_server_messages)
listening_thread.start()


def apply_background(window, image_path):
    window.bg_photo = ImageTk.PhotoImage(
        Image.open(image_path).resize((800, 900)))
    Label(window, image=window.bg_photo).place(
        x=0, y=0, relwidth=1, relheight=1)


root = ctk.CTk()
root.geometry("500x600+50+50")
root.title("")
root.resizable(False, False)
apply_background(root, "C:/MysteryDigitss.png")


def start_game():
    open_room_window()


start_button = ctk.CTkButton(
    root, command=start_game, width=200, height=50, corner_radius=50, fg_color="#4a0460", bg_color="#081029", hover_color="#24b4ed", background_corner_colors=("#091638", "#081537", "#080f2b", "#09102c"), text="Start Game", font=("Helvetica", 20, "bold"))
start_button.place(relx=0.5, rely=0.8, anchor="center")


def open_room_window():
    global room_window
    room_window = ctk.CTkToplevel(root)
    room_window.title("")
    room_window.geometry(root.geometry())
    apply_background(room_window, "C:/miga.png")
    create_room_widgets(room_window)
    root.withdraw()


def name_entries(window, name_pairs):
    name_widgets = []
    for index, (label_text, row, column) in enumerate(name_pairs):
        label = ctk.CTkButton(window, text=label_text, hover=False, corner_radius=20, background_corner_colors=(
            "#031f56", "#171945", "#2a295b", "#0c377a"), width=200, height=50, font=("Helvetica", 20, "bold"))
        label.grid(row=row, column=column, pady=30,
                   padx=20)
        window.grid_columnconfigure(column, weight=1)
        if label_text == "Player Two Name:":
            label.grid_remove()

        entry = ctk.CTkEntry(
            window, border_color="white", fg_color="#b7628d", bg_color="#dc86a8", justify='center', font=("Helvetica", 20, "bold"), width=200, height=50)
        entry.grid(row=row + 1, column=column, pady=30,
                   padx=20)
        name_widgets.append((label, entry))

    return name_widgets


def create_pin_widgets(window, pin_pairs):
    global player_one_pin_entries, player_two_pin_entries
    pin_widgets = []
    for index, (label_text, row, column) in enumerate(pin_pairs):
        label = ctk.CTkButton(window, text=label_text, hover=False,
                              corner_radius=20, font=("Helvetica", 20, "bold"), width=200, height=50, background_corner_colors=(
                                  "#f6a1bb", "#8cb9e1", "#4279c2", "#c27fa5"))
        label.grid(row=row, column=column + 1, pady=30, padx=20)
        pin_frame = ctk.CTkFrame(window, fg_color="#11296d", corner_radius=10)
        pin_frame.grid(row=row + 1, column=column + 1,
                       pady=30, padx=20)
        pin_entries = []
        for j in range(4):
            entry = ctk.CTkEntry(pin_frame, border_color="white", fg_color="#b7628d", bg_color="#1f6aa5", justify='center', font=(
                "Helvetica", 20, "bold"), width=40, height=50, validate="key", show="")
            entry.grid(row=0, column=j, padx=5, pady=5)
            pin_entries.append(entry)
        pin_widgets.append((label, pin_entries))

        if label_text == "Player Two PIN:":
            for entry in pin_entries:
                label.grid_forget()
            pin_frame.grid_forget()
    return pin_widgets


def open_data_entry_window(room_window):
    global name_widgets, pin_widgets
    data_entry_window = ctk.CTkToplevel(root)
    data_entry_window.title("")
    data_entry_window.geometry(root.geometry())
    apply_background(data_entry_window, "C:/miga.png")
    # Add additional widgets and functionality as needed

    name_pairs = [
        ("Player One Name:", 0, 1),   # Row 0, Column 0
    ]
    pin_pairs = [
        ("Player One PIN:", 2, 1),    # Row 2, Column 0
    ]
    name_widgets = name_entries(
        data_entry_window, name_pairs)
    pin_widgets = create_pin_widgets(data_entry_window, pin_pairs)

    def submit_player_data():
        global player_name, player_number, player_one_name, player_two_name
        player_name = name_widgets[0][1].get()
        print(f"player name is: {player_name}")
        client.send(f"player_name,{player_name}".encode("utf-8"))

        player_number = ''.join(entry.get() for entry in pin_widgets[0][1])
        print(f"player number is: {player_number}")
        client.send(f"player_number,{player_number}".encode("utf-8"))

        open_game_window(data_entry_window)

    start_button = ctk.CTkButton(
        data_entry_window, command=submit_player_data, text="Submit", width=200, height=50, corner_radius=50, fg_color="#4a0460", bg_color="#422160", hover_color="#24b4ed", background_corner_colors=("#321957", "#6c669d", "#565585", "#2c1657"), font=("Helvetica", 20, "bold"))
    start_button.place(relx=0.5, rely=0.8, anchor="center")

    room_window.withdraw()


def create_room_widgets(room_window):
    label_code = ctk.CTkLabel(
        room_window, text="Room Code: ", corner_radius=10, width=150, height=40)
    entry_code = ctk.CTkEntry(
        room_window, corner_radius=10, width=150, height=40)

    # Initially hide both widgets
    label_code.grid_forget()
    entry_code.grid_forget()

    def create_room():
        def thread_target():
            client.send("create,".encode("utf-8"))
            response = client.recv(1024).decode("utf-8")
            if "," in response:
                _, room_code = response.split(',')
                root.after(0, lambda: update_room_code_label(room_code))
            else:
                print("Invalid response format:", response)

        threading.Thread(target=thread_target).start()

    def update_room_code_label(room_code):
        label_code.configure(text=f"Room Code: {room_code}")
        label_code.grid(pady=40, padx=60)
        entry_code.grid_forget()

    def enter_room():
        entry_code.grid(pady=40, padx=60)
        label_code.grid_forget()

        def join_room():
            room_code = entry_code.get()
            client.send(f"join,{room_code}".encode("utf-8"))

        join_button = ctk.CTkButton(room_window, text="Join", command=join_room,
                                    corner_radius=20, font=("Helvetica", 15, "bold"), width=100, height=40)
        join_button.grid(pady=20, padx=60)

    create_room_button = ctk.CTkButton(room_window, text="Create Room", command=create_room,
                                       corner_radius=20, font=("Helvetica", 20, "bold"), width=200, height=50, background_corner_colors=(
                                           "#f6a1bb", "#8cb9e1", "#4279c2", "#c27fa5")
                                       )
    create_room_button.grid(pady=80, padx=150)

    enter_room_button = ctk.CTkButton(room_window, text="Enter Room", command=enter_room,
                                      corner_radius=20, font=("Helvetica", 20, "bold"), width=200, height=50, background_corner_colors=(
                                          "#f6a1bb", "#8cb9e1", "#4279c2", "#c27fa5")
                                      )
    enter_room_button.grid(pady=30, padx=40)


class CustomTable(tk.Frame):
    def __init__(self, parent, columns, row_height=30, header_bg_color="#ffffff", header_fg_color="#000000", row_bg_color="#ffffff", row_fg_color="#000000", font=('Helvetica', 14), **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = columns
        self.row_height = row_height
        self.header_bg_color = header_bg_color
        self.header_fg_color = header_fg_color
        self.row_bg_color = row_bg_color
        self.row_fg_color = row_fg_color
        self.font = font
        self.rows = []
        self.header_labels = []  # Store header labels
        self.create_headers()

    def create_headers(self):
        for i, col in enumerate(self.columns):
            self.columnconfigure(i, weight=1)  # Add this line
            label = ctk.CTkLabel(self, text=col, height=self.row_height, font=self.font,
                                 fg_color=self.row_bg_color, text_color=self.row_fg_color)
            label.grid(row=0, column=i, sticky='ew')
            self.header_labels.append(label)  # Append to header labels list

    def update_headers(self, new_headings):
        for label, new_text in zip(self.header_labels, new_headings):
            label.configure(text=new_text)

    def add_row(self, data, pin_columns=[0, 2]):
        row_num = len(self.rows) + 1
        row = []
        for i, item in enumerate(data):
            self.columnconfigure(i, weight=1)
            if i in pin_columns:
                pin_frame = ctk.CTkFrame(
                    self, fg_color=self.row_bg_color, corner_radius=10)
                pin_frame.grid(row=row_num, column=i, sticky='ew')
                pin_entries = []
                for j in range(4):
                    entry = ctk.CTkEntry(
                        pin_frame, justify='center', font=self.font, width=40, height=self.row_height)
                    entry.grid(row=0, column=j, padx=5, pady=5)
                    if j < len(item):
                        entry.insert(0, item[j])
                pin_entries.append(entry)
                row.append(pin_entries)
            else:
                label = ctk.CTkLabel(self, text=item, height=self.row_height, font=self.font,
                                     fg_color=self.row_bg_color, text_color=self.row_fg_color)
                label.grid(row=row_num, column=i, sticky='ew')
                row.append(label)
        self.rows.append(row)


def valid_pin_input(P):
    if P == "":
        return True
    try:
        value = int(P)
        return 1 <= value <= 20
    except ValueError:
        return False


def update_guess_labels():
    global guess_label_p1, guess_label_p2, player_one_name, player_two_name
    guess_label_p1.configure(
        text=f"{player_one_name}'s Guess:", font=("Helvetica", 20, "bold"))
    guess_label_p2.configure(
        text=f"{player_two_name}'s Guess:", font=("Helvetica", 20, "bold"))


def update_column_headings():
    global data_table, player_one_name, player_two_name
    new_headings = [f"{player_one_name}", "Result",
                    f"{player_two_name}", "Result"]
    data_table.update_headers(new_headings)


def open_game_window(data_entry_window):
    global game_data_table
    game_window = ctk.CTkToplevel()
    game_window.title("")
    game_window.geometry(root.geometry())
    apply_background(game_window, "C:/miga.png")

    columns = ['Numbers P1', 'Result P1', 'Numbers P2', 'Result P2']
    data_table = CustomTable(game_window, columns=columns,
                             font=('Helvetica', 16))
    data_table.pack(expand=False, fill='both')

    def create_guess_widgets(parent, label_text, fg_color_label, fg_color_entry):
        vcmd = (parent.register(valid_pin_input), '%P')
        label = ctk.CTkLabel(
            parent, text=label_text, fg_color=fg_color_label, corner_radius=10, width=150, height=40)
        guess_frame = ctk.CTkFrame(
            parent, fg_color=fg_color_entry, corner_radius=10)

        guess_entries = []
        for j in range(4):
            entry = ctk.CTkEntry(guess_frame, justify='center', font=(
                "Helvetica", 20, "bold"), width=40, height=50, validate="key", validatecommand=vcmd)
            entry.grid(row=0, column=j, padx=5, pady=5)
            guess_entries.append(entry)

        return label, guess_frame, guess_entries
    guess_label_p1, guess_frame_p1, guess_entries_p1 = create_guess_widgets(
        game_window, "Enter Your Guess:", "#e46796", "#11296d")
    guess_label_p2, guess_frame_p2, guess_entries_p2 = create_guess_widgets(
        game_window, "Player Two Guess:", "#e46796", "#11296d")
    guess_label_p1.place(x=50, y=400)  # Adjust x and y as needed
    guess_frame_p1.place(x=37, y=450)  # Adjust x and y as needed

    submit_guess_button = ctk.CTkButton(
        game_window,
        text="Submit Guess",
        command=lambda: submit_action(guess_frame_p1, guess_frame_p2,
                                      data_table, player_one_pin_entries, player_two_pin_entries),
        width=200, height=50)

    submit_guess_button.place(x=130, y=520)

    # Hide the previous window
    data_entry_window.withdraw()


def submit_action(frame_guess_p1, frame_guess_p2, data_table, player_one_pin_entries, player_two_pin_entries):
    global player_one_name, player_two_name

    def clear_entries(entries):
        for entry in entries:
            entry.delete(0, tk.END)

    def get_values_from_entries(entries):
        return [entry.get() for entry in entries]
    guess_for_p1 = get_values_from_entries(frame_guess_p1.winfo_children())
    guess_for_p2 = get_values_from_entries(frame_guess_p2.winfo_children())

    def get_pin_from_entries(entries):
        return [entry.get() for entry in entries]
    correct_pin_p1 = get_pin_from_entries(player_one_pin_entries)
    correct_pin_p2 = get_pin_from_entries(player_two_pin_entries)
    correct_guesses_p1 = sum(
        1 for guess in guess_for_p1 if guess in correct_pin_p2)
    correct_guesses_p2 = sum(
        1 for guess in guess_for_p2 if guess in correct_pin_p1)
    data_table.add_row([guess_for_p1, correct_guesses_p1,
                       guess_for_p2, correct_guesses_p2])
    clear_entries(frame_guess_p1.winfo_children())
    clear_entries(frame_guess_p2.winfo_children())
    if correct_guesses_p1 == len(correct_pin_p1):
        show_winner(player_one_name)
    elif correct_guesses_p2 == len(correct_pin_p2):
        show_winner(player_two_name)


def show_winner(winner_name):
    winner_window = ctk.CTkToplevel(root)
    winner_window.title("")
    congrats_label = ctk.CTkLabel(
        winner_window, text=f"Congratulations, {winner_name}! You win!")
    congrats_label.pack(pady=20)
    close_button = ctk.CTkButton(
        winner_window, text="Close", command=winner_window.destroy)
    close_button.pack(pady=10)
    winner_window.geometry("400x200+100+300")
    winner_window.grab_set()


root.mainloop()
