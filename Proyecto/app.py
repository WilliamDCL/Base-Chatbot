from flask import Flask, request, jsonify, render_template
import json
import os
from fuzzywuzzy import process
import webbrowser

app = Flask(__name__)

json_path = os.path.join(os.path.dirname(__file__), 'murales.json')
with open(json_path, 'r', encoding='utf-8') as f:
    murales = json.load(f)

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '').lower()

    if "iniciar" in question:
        return jsonify({"answer": "¡Estoy listo para responder tus preguntas!"})
    elif "termina" in question:
        return jsonify({"answer": "La conversación ha sido limpiada.", "reload": True})
    elif "abre navegador" in question:
        webbrowser.open('https://www.google.com')
        return jsonify({"answer": "Abriendo el navegador para hacer una consulta."})

    # Check for Google Maps location command
    if "ubicación en maps" in question or "abre en maps" in question:
        return abrir_maps(question)

    response = buscar_mural(question)

    if response:
        return jsonify(response)

    return jsonify({"answer": "Lo siento, no entendí tu pregunta. Intenta preguntar sobre un mural específico."})

def abrir_maps(question):
    mural_names = [mural['nombre'].lower() for mural in murales]
    matched_name = process.extractOne(question, mural_names)

    if matched_name and matched_name[1] > 70:  # Se encontró un mural similar
        mural = next(m for m in murales if m['nombre'].lower() == matched_name[0])
        # Construir la URL de Google Maps usando la ubicación del mural
        maps_url = f"https://www.google.com/maps/search/?api=1&query={mural['ubicacion'].replace(' ', '+')},+Tunja,+Boyacá,+Colombia"
        
        # Abrir la URL en una nueva ventana del navegador
        webbrowser.open(maps_url)
        
        return {"answer": f"Abriendo la ubicación del mural '{mural['nombre']}' en Google Maps."}

    return {"answer": "No pude encontrar la ubicación del mural en Maps."}


def buscar_mural(question):
    mural_names = [mural['nombre'].lower() for mural in murales]
    mural_artists = [mural['artista'].lower() for mural in murales]

    year = None
    for word in question.split():
        if word.isdigit() and 1900 <= int(word) <= 2023:  
            year = int(word)
            break

    matched_name = process.extractOne(question, mural_names)
    matched_artist = process.extractOne(question, mural_artists)

    if matched_name and matched_name[1] > 70: 
        mural = next(m for m in murales if m['nombre'].lower() == matched_name[0])

        if any(keyword in question for keyword in ["describe", "cuéntame", "háblame de"]):
            response = {
                "answer": f"El mural '{mural['nombre']}' fue realizado por {mural['artista']} en {mural['fecha']}. Descripción: {mural['descripcion']}."
            }
            return response
        elif any(keyword in question for keyword in ["dirección", "ubicación", "dónde está"]):
            response = {
                "answer": f"La dirección del mural '{mural['nombre']}' es {mural['ubicacion']}."
            }
            return response

    if matched_artist and matched_artist[1] > 70:
        artist_murals = [m for m in murales if m['artista'].lower() == matched_artist[0]]
        if artist_murals:
            return {
                "answer": f"El artista '{matched_artist[0]}' ha creado los siguientes murales: " + ', '.join([m['nombre'] for m in artist_murals]) + "."
            }

    if year:
        year_murals = [m for m in murales if m['fecha'] == str(year)]
        if year_murals:
            return {
                "answer": f"Los murales creados en {year} son: " + ', '.join([m['nombre'] for m in year_murals]) + "."
            }

    return None

if __name__ == '__main__':
    app.run(debug=True)
