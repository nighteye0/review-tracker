from flask import Flask
from flask_cors import CORS
import requests
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

tokens = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "DOGE": "dogecoin", "PEPE": "pepe"}
emojis = {"BTC": "🟠", "ETH": "🔵", "SOL": "🟣", "DOGE": "🐕", "PEPE": "🐸"}

token_data = {}
print("Loading tokens...")
ids = ",".join(tokens.values())
try:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    response = requests.get(url, timeout=10).json()
    for symbol, token_id in tokens.items():
        if token_id in response:
            data = response[token_id]
            price = data.get("usd", 0)
            token_data[symbol] = {"emoji": emojis[symbol], "price": f"${price:,.2f}", "change": f"{data.get('usd_24h_change', 0):+.2f}%"}
            print(f"OK {symbol}")
except Exception as e:
    print(f"Error: {e}")

@app.route("/")
def index():
    cards = ""
    for symbol, data in token_data.items():
        cards += f"<div style='border:2px solid #0f0;padding:15px;margin:10px;'>{data['emoji']} {symbol} {data['price']} {data['change']}</div>"
    
    token_json = json.dumps(token_data)
    
    return f"""
    <html>
    <head><title>Dashboard</title></head>
    <body style="background:#0f0c29;color:#00ff88;font-family:Courier;padding:20px;">
        <h1>Dashboard</h1>
        <input id="search" type="text" placeholder="Search..." style="width:100%;padding:10px;margin:20px 0;background:#000;color:#0f0;border:2px solid #0f0;">
        <div id="results"></div>
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;">
        {cards}
        </div>
        <script>
        let tokens = {token_json};
        document.getElementById('search').onkeyup = function(e) {{
            let q = e.target.value.toUpperCase();
            let r = document.getElementById('results');
            if (!q) {{
                r.innerHTML = '';
                return;
            }}
            let matches = Object.keys(tokens).filter(k => k.includes(q));
            r.innerHTML = matches.map(k => '<div style="padding:10px;border:1px solid #0f0;margin:5px;cursor:pointer;">' + tokens[k].emoji + ' ' + k + ' ' + tokens[k].price + '</div>').join('');
        }};
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("\n🚀 Dashboard at http://localhost:9000\n")
    app.run(debug=False, port=9000, use_reloader=False)
