import socket
import threading
import re
import random
from influxdb_client import InfluxDBClient, Point, WritePrecision

HOST = "0.0.0.0"
PUERTO = 5000

usuarios = {}
jugadores = []          # lista de tuplas (conn, nick)
puntos = {}

respuestas_correctas = {
    "1": "b", "2": "c", "3": "c", "4": "a", "5": "b",
    "6": "c", "7": "b", "8": "c", "9": "b", "10": "d",
    "11": "a", "12": "a", "13": "b", "14": "b", "15": "c",
    "16": "d", "17": "b", "18": "b", "19": "b", "20": "b"
}

def email_valido(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# ───────── InfluxDB ─────────
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "MKhlN06e1kFiFMr-egOXAwVUO-azy_usypUIAInvKb-RBhZxe9RQoTLEshBGt7XppsRDtqg4oMJSv5WbNYeC2A=="
INFLUX_ORG = "PSP"
INFLUX_BUCKET_PREG = "trivial"
INFLUX_BUCKET_CLASIF = "clasifiaciones"

inicio_juego = threading.Event()
preguntas_seleccionadas = []

# ───────── Leer preguntas ─────────
def leer_preguntas():
    preguntas = []
    try:
        with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
            query_api = client.query_api()
            query = f'''
            from(bucket:"{INFLUX_BUCKET_PREG}")
              |> range(start: -1y)
              |> filter(fn: (r) => r._measurement == "pregunta")
            '''
            result = query_api.query(query)

            for table in result:
                for record in table.records:
                    num = str(record.values["numero"])
                    p = next((q for q in preguntas if q["numero"] == num), None)
                    if not p:
                        p = {"numero": num, "texto": "", "a": "", "b": "", "c": "", "d": ""}
                        preguntas.append(p)
                    p[record.get_field()] = record.get_value()

    except Exception as e:
        print("Error leyendo preguntas:", e)

    return preguntas

# ───────── Guardar clasificación partida ─────────
def guardar_clasificacion(puntos_partida):
    try:
        with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
            write_api = client.write_api(write_precision=WritePrecision.S)
            for nick, pts in puntos_partida.items():
                point = (
                    Point("partida")
                    .tag("nick", nick)
                    .field("puntos", pts)
                )
                write_api.write(bucket=INFLUX_BUCKET_CLASIF, record=point)
    except Exception as e:
        print("Error guardando clasificación:", e)

# ───────── Leer clasificación general ─────────
def leer_clasificacion_general():
    ranking = {}
    try:
        with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
            query_api = client.query_api()
            query = f'''
            from(bucket:"{INFLUX_BUCKET_CLASIF}")
              |> range(start: -10y)
              |> filter(fn: (r) => r._measurement == "partida")
            '''
            result = query_api.query(query)

            for table in result:
                for record in table.records:
                    nick = record.values["nick"]
                    ranking[nick] = ranking.get(nick, 0) + record.get_value()

    except Exception as e:
        print("Error leyendo clasificación:", e)

    return sorted(ranking.items(), key=lambda x: x[1], reverse=True)

# ───────── Cliente ─────────
def manejar_cliente(conn, addr):
    try:
        conn.send("Bienvenido al Trivial!\n".encode())

        while True:
            conn.send("Ingrese email: ".encode())
            email = conn.recv(1024).decode().strip()
            if not email_valido(email):
                conn.send("Email inválido.\n".encode())
                continue
            conn.send("Ingrese contraseña: ".encode())
            password = conn.recv(1024).decode().strip()
            usuarios[email] = password
            break

        conn.send("Ingrese su Nick para la partida: ".encode())
        nick = conn.recv(1024).decode().strip()

        jugadores.append((conn, nick))
        puntos[nick] = 0

        conn.send(f"Esperando jugadores... ({len(jugadores)}/4)\n".encode())
        print(f"{nick} conectado ({len(jugadores)}/4)")

        if len(jugadores) == 4:
            global preguntas_seleccionadas
            todas = leer_preguntas()
            preguntas_seleccionadas = random.sample(todas, 5)
            inicio_juego.set()

        inicio_juego.wait()

    except Exception as e:
        print("Error cliente:", e)

# ───────── Coordinador ─────────
def juego_coordinador():
    inicio_juego.wait()

    for pregunta in preguntas_seleccionadas:
        mensaje = (
            f"\nPREGUNTA {pregunta['numero']}: {pregunta['texto']}\n"
            f"a) {pregunta['a']}  b) {pregunta['b']}  "
            f"c) {pregunta['c']}  d) {pregunta['d']}\n"
        )

        for c, _ in jugadores:
            c.send(mensaje.encode())

        respuestas = {}
        for c, n in jugadores:
            c.send("Tu respuesta: ".encode())
            respuestas[n] = c.recv(1024).decode().strip().lower()

        correcta = respuestas_correctas[pregunta["numero"]]
        for c, n in jugadores:
            if respuestas[n] == correcta:
                puntos[n] += 1
                c.send("✅ Correcta!\n".encode())
            else:
                c.send(f"❌ Incorrecta. Respuesta correcta: {correcta}\n".encode())

    # ───────── Resultados partida (clientes) ─────────
    ranking = sorted(puntos.items(), key=lambda x: x[1], reverse=True)
    final = "\n🏁 RESULTADOS PARTIDA 🏁\n"
    for i, (n, p) in enumerate(ranking, 1):
        final += f"{i}. {n} -> {p} puntos\n"

    for c, _ in jugadores:
        c.send(final.encode())

    # Guardar clasificación
    guardar_clasificacion(puntos)

    # ───────── Clasificación general SOLO servidor ─────────
    general = leer_clasificacion_general()

    print("\n🏆 CLASIFICACIÓN GENERAL (SERVIDOR) 🏆")
    for i, (n, p) in enumerate(general, 1):
        print(f"{i}. {n} -> {p} puntos")

    for c, _ in jugadores:
        c.close()

    jugadores.clear()
    puntos.clear()
    preguntas_seleccionadas.clear()
    inicio_juego.clear()

# ───────── Servidor ─────────
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PUERTO))
server.listen(5)
print("Servidor iniciado...")

threading.Thread(target=juego_coordinador, daemon=True).start()

while True:
    conn, addr = server.accept()
    if len(jugadores) >= 4:
        conn.send("Partida llena.\n".encode())
        conn.close()
    else:
        threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True).start()
