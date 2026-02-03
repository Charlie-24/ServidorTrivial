# Trivial Cliente-Servidor en Python

## Descripción del proyecto
Este proyecto consiste en el desarrollo de una **aplicación cliente-servidor en Python** que permite jugar a un **trivial multijugador**.  
El sistema está diseñado para ejecutarse en **máquinas virtuales**, alojando el servidor y los clientes de forma independiente.

El servidor gestiona una única partida de trivial formada por **exactamente cuatro jugadores**, impidiendo el acceso a cualquier usuario adicional.

---

## Gestión de usuarios
- Los usuarios deben **registrarse** utilizando un **email y una contraseña**.
- El sistema valida que:
  - El email tenga un formato correcto.
  - El email sea único y no esté previamente registrado.
- Tras iniciar sesión, cada usuario introduce un **Nick** con el que participará en la partida.

---

## Funcionamiento del juego
1. El servidor queda a la espera hasta que se conectan **cuatro jugadores registrados**.
2. Cada cliente recibe un mensaje indicando que debe esperar a otros jugadores.
3. Se muestran los **Nicks de los jugadores** que formarán parte de la partida.
4. El servidor muestra en consola los Nicks de los jugadores conectados.
5. Cuando los cuatro jugadores están listos:
   - Se seleccionan **5 preguntas aleatorias** de un total de **20 preguntas** almacenadas en un fichero o base de datos.
   - Cada pregunta contiene:
     - Enunciado.
     - Cuatro posibles respuestas.
     - Una única respuesta correcta.
6. Cada jugador responde a las preguntas de forma individual.
7. Tras cada respuesta, el sistema indica si es **correcta o incorrecta**.

---

## 🏆 Puntuación y resultados
- Cada respuesta correcta suma **1 punto**.
- Al finalizar la partida:
  - Se muestra al usuario su **puntuación total**.
  - Se muestran las puntuaciones de los **cuatro jugadores**.
  - Se indica si el jugador ha **ganado o perdido** la partida.
- El servidor mantiene una **clasificación general** con los resultados de todas las partidas jugadas.

---

## Arquitectura
- Aplicación basada en el modelo **cliente-servidor**.
- Servidor y clientes ejecutándose en **máquinas virtuales**.
- El servidor controla:
  - Conexiones.
  - Autenticación.
  - Desarrollo de la partida.
  - Clasificación global.

---


