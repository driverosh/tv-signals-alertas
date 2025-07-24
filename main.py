from flask import Flask, request
import time
import requests
import os
from collections import deque

app = Flask(__name__)

# Telegram config
TELEGRAM_TOKEN = '7987965778:AAGTlTvYdUIw-O2F5kjopasav7B1FmKEyok'
CHAT_ID = '8155134155'

# Señales recibidas recientemente (últimos 5 minutos máx)
señales = deque(maxlen=100)

@app.route('/')
def home():
    return "Servidor activo ✅"

@app.route('/webhook', methods=['POST'])
def webhook():
    print("🔥 Webhook recibido", flush=True)

    body = request.data.decode('utf-8')
    print("🔍 Body:", body, flush=True)

    try:
        data = request.get_json(force=True)
        source = data.get('source')
        if not source:
            print("⚠️ Alerta ignorada: 'source' vacío o ausente", flush=True)
            return 'Missing source', 400

        ahora = time.time()
        señales.append({'source': source, 'timestamp': ahora})
        print(f"📩 [{source}] recibida a las {time.strftime('%H:%M:%S')}", flush=True)

        # Filtrar señales de los últimos 5 minutos
        recientes = [s for s in señales if ahora - s['timestamp'] < 300]
        fuentes = set(s['source'] for s in recientes)

        # Señal ALCISTA completa
        if {'OG Long', 'Bullish FVG', 'Bullish CHoCH'}.issubset(fuentes):
            enviar_alerta("✅ Señal ALCISTA: OG Long + Bullish FVG + CHoCH")
            limpiar_señales(['OG Long', 'Bullish FVG', 'Bullish CHoCH'], recientes)

        # Señal BAJISTA completa
        if {'OG Short', 'Bearish FVG', 'Bearish CHoCH'}.issubset(fuentes):
            enviar_alerta("🔻 Señal BAJISTA: OG Short + Bearish FVG + CHoCH")
            limpiar_señales(['OG Short', 'Bearish FVG', 'Bearish CHoCH'], recientes)

    except Exception as e:
        print("❌ Error al parsear JSON:", str(e), flush=True)
        return 'Invalid JSON', 400

    return '', 200

def limpiar_señales(targets, recientes):
    global señales
    señales.extend([s for s in recientes if s['source'] not in targets])

def enviar_alerta(mensaje):
    print("🚨 Enviando alerta a Telegram:", mensaje, flush=True)
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensaje}
    response = requests.post(url, data=payload)
    print("📤 Respuesta Telegram:", response.status_code, response.text, flush=True)

# Inicio para entorno Render u otro
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
