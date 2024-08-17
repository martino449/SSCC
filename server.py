import socket
import threading

clients = []
client_usernames = {}

def handle_client(client_socket, client_address):
    print(f"[+] Nuova connessione da {client_address}")
    clients.append(client_socket)

    client_socket.send("Inserisci il tuo username:".encode('utf-8'))
    username = client_socket.recv(1024).decode('utf-8')
    client_usernames[client_socket] = username
    broadcast_message(f"[{username}] è entrato in chat.", client_socket)

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message.startswith("FILE:"):
                file_name = message.split(":")[1]
                receive_file(client_socket, file_name)
            elif message.startswith("PM:"):
                recipient, private_message = message.split(":")[1:3]
                send_private_message(username, recipient, private_message)
            elif message == "LIST":
                send_user_list(client_socket)
            elif message == "HELP":
                send_help(client_socket)
            else:
                broadcast_message(f"{username}: {message}", client_socket)
        except:
            print(f"[-] Connessione persa da {client_address}")
            clients.remove(client_socket)
            broadcast_message(f"[{username}] ha lasciato la chat.", client_socket)
            client_usernames.pop(client_socket, None)
            client_socket.close()
            break

def receive_file(client_socket, file_name):
    with open(file_name, "wb") as f:
        while True:
            file_data = client_socket.recv(1024)
            if not file_data:
                break
            f.write(file_data)
    print(f"[+] File {file_name} ricevuto con successo")

def broadcast_message(message, exclude_socket=None):
    for client in clients:
        if client != exclude_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                clients.remove(client)
                client_usernames.pop(client, None)
                client.close()

def send_private_message(sender_username, recipient_username, message):
    for client, username in client_usernames.items():
        if username == recipient_username:
            try:
                client.send(f"[PM da {sender_username}]: {message}".encode('utf-8'))
            except:
                client.close()
                clients.remove(client)
                client_usernames.pop(client, None)
            return
    # Se l'utente non è trovato
    for client, username in client_usernames.items():
        if username == sender_username:
            client.send(f"[-] Utente {recipient_username} non trovato.".encode('utf-8'))

def send_user_list(client_socket):
    user_list = "Utenti online:\n" + "\n".join(client_usernames.values())
    client_socket.send(user_list.encode('utf-8'))

def send_help(client_socket):
    help_message = """
    Comandi disponibili:
      LIST - Mostra la lista degli utenti online
      PM:<username>:<message> - Invia un messaggio privato
      FILE:<filename> - Invia un file al server
      HELP - Mostra questo elenco di comandi
    """
    client_socket.send(help_message.encode('utf-8'))

def accept_clients(server):
    while True:
        client_socket, client_address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

def start_server(host="0.0.0.0", port=5555):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[+] Server in ascolto su {host}:{port}")

    accept_thread = threading.Thread(target=accept_clients, args=(server,))
    accept_thread.start()

    while True:
        message = input("SERVER: ")
        broadcast_message(f"SERVER: {message}")

if __name__ == "__main__":
    start_server()
