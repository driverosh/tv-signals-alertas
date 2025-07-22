from flask import Flask, request
import time
import requests

app = Flask(__name__)

# 👇 Reemplaza con tu bot y chat real
TELEGRAM_TOKEN = '7987965778:AAGTlTvYdUIw-O2F5kjopasav7B1FmKEyok'
CHAT_ID = '8155134155'

# Registro de señales
señales = []

@app.route('/')
def home():
    return "Servidor activo ✅"

@app.route('/webhook', methods=['POST'])
def webhook():
    print("🔍 Headers:", dict(request.headers))
    print("🔍 Body:", request.data.decode('utf-8'))
    
    try:
        data = request.get_json(force=True)
        print("📩 Alerta recibida:", data)
    except Exception as e:
        print("❌ Error al parsear JSON:", str(e))
        return 'Invalid JSON', 400


    ahora = time.time()
    señales.append({
        'source': data.get('source'),
        'timestamp': ahora
    })

    # Filtrar señales de últimos 5 minutos
    recientes = [s for s in señales if ahora - s['timestamp'] < 300]
    fuentes = set(s['source'] for s in recientes)

    # Detectar señal alcista: OG Long + Bullish FVG
    if {'OG Long', 'Bullish FVG'}.issubset(fuentes):
        enviar_alerta("✅ Señal ALCISTA: OG Long + Bullish FVG")
        señales.clear()

    # Detectar señal bajista: OG Short + Bearish FVG
    if {'OG Short', 'Bearish FVG'}.issubset(fuentes):
        enviar_alerta("🔻 Señal BAJISTA: OG Short + Bearish FVG")
        señales.clear()

    return '', 200

def enviar_alerta(mensaje):
    print("🚨 Enviando alerta:", mensaje)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': mensaje})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

