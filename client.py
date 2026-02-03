import socket
import threading

HOST = "172.20.10.2"  # IP del servidor
PUERTO = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PUERTO))
    print("Conectado al servidor.")
except Exception as e:
    print(f"No se pudo conectar al servidor: {e}")
    exit()

def recibir_mensajes():
    while True:
        try:
            msg = client.recv(1024).decode("utf-8")
            if msg:
                print(msg)
        except Exception as e:
            print("Conexión cerrada por el servidor.")
            break

# Hilo para recibir mensajes del servidor
threading.Thread(target=recibir_mensajes, daemon=True).start()

# Enviar mensajes / respuestas
while True:
    try:
        msg = input()

        # Si es respuesta, normalizar a minúscula
        if msg.lower() in ["a", "b", "c", "d"]:
            client.send(msg.lower().encode("utf-8"))
        else:
            client.send(msg.encode("utf-8"))

    except Exception as e:
        print("Error al enviar datos al servidor.")
        break
