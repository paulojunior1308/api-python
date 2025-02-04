from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Permite chamadas do front-end

GOOGLE_PLACES_API_KEY = "AIzaSyCp8RmS90f1JMPlQXqbOoOco9wr2_Eripg"

def buscar_estabelecimentos(cidade):
    """Busca estabelecimentos na cidade e obtém detalhes."""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    tipos = ["restaurant", "pizzeria", "churrascaria", "pastelaria"]
    query = f"{' OR '.join(tipos)} em {cidade}"
    params = {"query": query, "key": GOOGLE_PLACES_API_KEY}
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "results" not in data:
        return []
    
    estabelecimentos = []
    for place in data["results"]:
        place_id = place.get("place_id")
        nome = place.get("name", "Nome não encontrado")
        detalhes = buscar_detalhes_place(place_id) if place_id else {}
        
        endereco = detalhes.get("formatted_address", "Endereço não disponível")
        telefone = detalhes.get("formatted_phone_number", "Telefone não disponível")
        instagram = buscar_instagram(nome, cidade)
        
        estabelecimentos.append({
            "nome": nome,
            "telefone": telefone,
            "endereço": endereco,
            "instagram": instagram
        })
    
    return estabelecimentos

def buscar_detalhes_place(place_id):
    """Busca detalhes do estabelecimento."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"place_id": place_id, "fields": "formatted_address,formatted_phone_number", "key": GOOGLE_PLACES_API_KEY}
    response = requests.get(url, params=params)
    return response.json().get("result", {})

def buscar_instagram(nome, cidade):
    """Busca link do Instagram via Google."""
    busca = f"{nome} {cidade} site:instagram.com"
    url = f"https://www.google.com/search?q={busca}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Não encontrado"
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    for link in links:
        href = link.get("href", "")
        if "instagram.com" in href:
            return href.split("&")[0].replace("/url?q=", "")
    
    return "Não encontrado"

@app.route("/api/establishments", methods=["GET"])
def api_establishments():
    cidade = request.args.get("city")
    if not cidade:
        return jsonify({"error": "Parâmetro 'city' é obrigatório"}), 400
    
    estabelecimentos = buscar_estabelecimentos(cidade)
    return jsonify(estabelecimentos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
