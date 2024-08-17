import socket
import threading
import os

def send_messages(client_socket):
    while True:
        message = input("> ")
        if message.startswith("FILE:"):
            file_name = message.split(":")[1]
            send_file(client_socket, file_name)
        elif message.startswith("PM:"):
            client_socket.send(message.encode('utf-8'))
        elif message == "LIST" or message == "HELP":
            client_socket.send(message.encode('utf-8'))
        else:
            client_socket.send(message.encode('utf-8'))

def send_file(client_socket, file_name):
    if os.path.exists(file_name):
        client_socket.send(f"FILE:{file_name}".encode('utf-8'))
        with open(file_name, "rb") as f:
            while True:
                file_data = f.read(1024)
                if not file_data:
                    break
                client_socket.send(file_data)
        print(f"[+] File {file_name} inviato con successo")
    else:
        print("[-] File non trovato")

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(f"\n{message}")
        except:
            print("[-] Connessione al server persa")
            client_socket.close()
            break

def start_client(host="127.0.0.1", port=5555):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    send_thread = threading.Thread(target=send_messages, args=(client,))
    receive_thread = threading.Thread(target=receive_messages, args=(client,))

    send_thread.start()
    receive_thread.start()

if __name__ == "__main__":
    print("Comandi disponibili:")
    print("  LIST - Mostra la lista degli utenti online")
    print("  PM:<username>:<message> - Invia un messaggio privato")
    print("  FILE:<filename> - Invia un file al server")
    print("  HELP - Mostra questo elenco di comandi")
    start_client()
