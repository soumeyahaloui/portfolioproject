import socket
import threading
import random
import json  # Import JSON module


# Server configuration
host = '127.0.0.1'  # localhost
port = 65432

# Global dictionary to hold rooms
rooms = {}
client_data = {}  # Stores data for each client, indexed by their address
players_data = {'creator': None, 'joiner': None}


# Function to broadcast messages to all clients in a room

def game_room_server(name, client_conn):
    while True:
        data = client_conn.recv(1024).decode("utf-8")
        if not data:
            break
        print(f"{name} received data: {data}")


def broadcast(room_code, message):
    for client_conn in rooms.get(room_code, []):
        try:
            client_conn.send(message.encode("utf-8"))
        except Exception as e:
            print(f"Error sending message: {e}")

# Function to handle individual client connections


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    client_data[addr] = {"name": None, "number": None, "other_data": {}}

    try:
        while True:
            # Receive data from client
            data = receive_client_data(conn)
            if not data:
                break

            try:
                # Try to parse the data as JSON
                player_data = json.loads(data)
                role = player_data.get('role')

                # Store data based on role
                if role == 'creator':
                    players_data['creator'] = player_data
                elif role == 'joiner':
                    players_data['joiner'] = player_data

                # Logic to send data to the other player

                # Logic to send data to the other player
                room_code = find_room_code_for_connection(conn)

                if players_data['creator'] and players_data['joiner']:
                    # Send creator data to joiner and joiner data to creator
                    for client_conn in rooms.get(room_code, []):
                        if client_conn != conn:  # If not the current client
                            if role == 'creator' and players_data['joiner']:
                                conn.send(json.dumps(
                                    players_data['joiner']).encode('utf-8'))
                            elif role == 'joiner' and players_data['creator']:
                                conn.send(json.dumps(
                                    players_data['creator']).encode('utf-8'))

            except json.JSONDecodeError:
                # If it's not JSON, process it as a regular command
                # Split only on the first comma
                data_parts = data.split(",", 1)
                if len(data_parts) != 2:
                    print("Invalid data format received.")
                    continue

                command, room_code = data_parts
                process_client_command(command, room_code, conn, addr)

    except Exception as e:
        print(f"Error in client connection: {e}")
    finally:
        conn.close()
        remove_client_from_rooms(conn)
        del client_data[addr]  # Remove client data when disconnecting


def receive_client_data(conn):
    try:
        data = conn.recv(1024).decode("utf-8")
        return data
    except Exception as e:
        print(f"Error receiving data: {e}")
        return None


def process_client_command(command, room_code, conn, addr):

    if command == 'create':
        handle_create_room(conn, addr)
    elif command == 'join':
        handle_join_room(room_code, conn, addr)
    elif command == 'player_name':
        handle_player_name(room_code, conn, addr)
    elif command == 'player_number':
        handle_player_number(room_code, conn, addr)


def handle_create_room(conn, addr):
    room_code = str(random.randint(1000, 9999))
    rooms[room_code] = [conn]
    client_data[addr]['role'] = 'creator'  # Assign role as creator

    conn.send(f"ROOM_CREATED,{room_code}".encode("utf-8"))


def handle_join_room(room_code, conn, addr):
    if room_code in rooms and len(rooms[room_code]) < 2:
        rooms[room_code].append(conn)
        client_data[addr]['role'] = 'joiner'  # Assign role as joiner

        if len(rooms[room_code]) == 2:
            broadcast(room_code, "START_GAME")
    else:
        conn.send("ROOM_NOT_FOUND_OR_FULL".encode("utf-8"))


def handle_player_name(name, conn, addr):
    client_data[addr]["name"] = name


def handle_player_number(number, conn, addr):
    try:
        # Convert the received number to an integer
        number = int(number)
        client_data[addr]["number"] = number
        print_client_data(addr)

    except ValueError:
        print(f"Invalid player number received from {addr}")


def print_client_data(addr):
    print(f"Data for client {addr}: {client_data[addr]}")


def find_room_code_for_connection(conn):
    for room_code, clients in rooms.items():
        if conn in clients:
            return room_code
    return None  # Return None if the connection is not found in any room


# Function to remove a client from all rooms


def remove_client_from_rooms(client_conn):
    for room_code, clients in rooms.items():
        if client_conn in clients:
            clients.remove(client_conn)
            # Optional: Close room if empty
            if not clients:
                del rooms[room_code]
            break

# Function to start the server


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[LISTENING] Server is listening on {host}:{port}")

    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except Exception as e:
            print(f"Error accepting new connection: {e}")


# Run the server
start_server()
