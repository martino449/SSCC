import socket
import threading

# Lista per tenere traccia dei client connessi
clients = []

# Funzione per gestire i messaggi dei client
def handle_client(client_socket, client_address):
    print(f"[+] Nuova connessione da {client_address}")
    clients.append(client_socket)
    
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message.startswith("FILE"):
                file_name = message.split(":")[1]
                receive_file(client_socket, file_name)
            else:
                print(f"{client_address}: {message}")
                # Potresti voler ritrasmettere il messaggio agli altri client
        except:
            print(f"[-] Connessione persa da {client_address}")
            clients.remove(client_socket)
            client_socket.close()
            break

# Funzione per ricevere un file
def receive_file(client_socket, file_name):
    with open(file_name, "wb") as f:
        while True:
            file_data = client_socket.recv(1024)
            if not file_data:
                break
            f.write(file_data)
    print(f"[+] File {file_name} ricevuto con successo")

# Funzione per inviare un messaggio a tutti i client connessi
def broadcast_message(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            # Rimuovere client che non rispondono
            clients.remove(client)
            client.close()

# Avvio del server
def start_server(host="0.0.0.0", port=5555):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[+] Server in ascolto su {host}:{port}")

    # Thread per accettare connessioni client
    accept_thread = threading.Thread(target=accept_clients, args=(server,))
    accept_thread.start()

    # Permettere al server di inviare messaggi
    while True:
        message = input("SERVER: ")
        broadcast_message(f"SERVER: {message}")

# Funzione per accettare i client in un thread separato
def accept_clients(server):
    while True:
        client_socket, client_address = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()

if __name__ == "__main__":
    start_server()
