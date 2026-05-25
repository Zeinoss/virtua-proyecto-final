from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import abort
import os

app = Flask(__name__)
CORS(app)

mongo_host = os.getenv("MONGO_HOST", "mongo")
mongo_port = int(os.getenv("MONGO_PORT", 27017))
mongo_user = os.getenv("MONGO_USER", "admin")
mongo_password = os.getenv("MONGO_PASSWORD", "Admin12345")
mongo_db = os.getenv("MONGO_DB", "proyecto_db")

mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/?authSource=admin"

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db["jugadores"]


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Backend Flask funcionando correctamente"
    })

@app.route("/api/jugadores", methods=["POST"])
def crear_jugador():
    data = request.get_json()

    nombre = data.get("nombre", "").strip()
    tag = data.get("tag", "").strip()
    ciudad = data.get("ciudad", "").strip()
    main = data.get("main", "").strip()

    if not nombre or not tag or not ciudad or not main:
        return jsonify({
            "error": "Todos los campos son obligatorios"
        }), 400

    nuevo_jugador = {
        "nombre": nombre,
        "tag": tag,
        "ciudad": ciudad,
        "main": main,
        "puntuacion": 0  # <-- agregamos puntuación inicial en 0
    }

    resultado = collection.insert_one(nuevo_jugador)

    jugador_respuesta = {
        "id": str(resultado.inserted_id),
        "nombre": nombre,
        "tag": tag,
        "ciudad": ciudad,
        "main": main,
        "puntuacion": 0
    }

    return jsonify({
        "message": "Jugador guardado correctamente",
        "jugador": jugador_respuesta
    }), 201


@app.route("/api/jugadores", methods=["GET"])
def obtener_jugadores():
    jugadores = []

    for jugador in collection.find().sort("_id", 1):
        jugadores.append({
            "id": str(jugador["_id"]),
            "nombre": jugador.get("nombre", ""),
            "tag": jugador.get("tag", ""),
            "ciudad": jugador.get("ciudad", ""),
            "main": jugador.get("main", ""),
            "puntuacion": jugador.get("puntuacion", 0)
        })

    return jsonify(jugadores)

    return jsonify(jugadores)

# Endpoint para actualizar puntuación
@app.route("/api/jugadores/actualizar", methods=["POST"])
def actualizar_puntuacion():
    data = request.get_json()
    tag = data.get("tag", "").strip()
    puntos = int(data.get("puntos", 0))

    if not tag:
        return jsonify({"error": "Se requiere el tag"}), 400

    jugador = collection.find_one({"tag": tag})
    if not jugador:
        return jsonify({"error": "Jugador no encontrado"}), 404

    nuevo_puntaje = jugador.get("puntuacion", 0) + puntos
    collection.update_one({"tag": tag}, {"$set": {"puntuacion": nuevo_puntaje}})

    return jsonify({
        "message": f"Puntuación actualizada a {nuevo_puntaje}",
        "jugador": {"tag": tag, "puntuacion": nuevo_puntaje}
    })

# Endpoint para borrar jugador
@app.route("/api/jugadores/borrar", methods=["POST"])
def borrar_jugador():
    data = request.get_json()
    tag = data.get("tag", "").strip()

    if not tag:
        return jsonify({"error": "Se requiere el tag"}), 400

    resultado = collection.delete_one({"tag": tag})
    if resultado.deleted_count == 0:
        return jsonify({"error": "Jugador no encontrado"}), 404

    return jsonify({"message": f"Jugador con tag '{tag}' eliminado"})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)