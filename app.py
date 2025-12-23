import os
import requests
from flask import Flask, redirect, request, url_for, render_template_string

# ==========================================================
# 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 SYSTEM WERYFIKACJI - POPRAWIONA KONFIGURACJA
# ==========================================================
CLIENT_ID = "1450934033935765675" # Poprawione (usunięte zbędne cyfry na końcu)
CLIENT_SECRET = "F207SC3VEztN0qZCwRNPFG9PJtRg2lX-"
BOT_TOKEN = "MTQ1MDkzNDAzMzkzNTc2NTY3NQ.Ggw5dp.hTTDk-m5YZ_XB4Aw_UqhhUPOW5gv2GFCEUTQzY"
GUILD_ID = "1451263520661311608"
ROLE_ID = "1451263520812568672"
REDIRECT_URI = "http://localhost:5000/callback" # TO MUSI BYĆ TAKIE SAME W PANELU DISCORD

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Funkcja ładująca Twój plik HTML
def load_html():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Błąd: Plik index.html musi być w tym samym folderze!</h1>"

@app.route('/')
def home():
    return render_template_string(load_html())

@app.route('/login')
def login():
    # URL do autoryzacji - prosi tylko o identyfikację (identify)
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return redirect(url_for('home', status='error'))

    # 1. Wymiana kodu na Access Token
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        r = requests.post('https://discord.com/api/v10/oauth2/token', data=data, headers=headers)
        r.raise_for_status()
        token = r.json().get('access_token')

        # 2. Pobranie ID użytkownika
        user_r = requests.get('https://discord.com/api/v10/users/@me', headers={'Authorization': f'Bearer {token}'})
        user_id = user_r.json().get('id')

        # 3. Nadanie rangi przez bota
        bot_headers = {'Authorization': f'Bot {BOT_TOKEN}'}
        verify_url = f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user_id}/roles/{ROLE_ID}"
        
        res = requests.put(verify_url, headers=bot_headers)

        if res.status_code in [200, 204]:
            return redirect(url_for('home', status='success'))
        else:
            print(f"Błąd Discord API: {res.text}")
            return redirect(url_for('home', status='error'))
            
    except Exception as e:
        print(f"Błąd: {e}")
        return redirect(url_for('home', status='error'))

if __name__ == '__main__':
    print("--- System 𝑺𝒘𝒊𝒓𝑯𝒖𝒃 gotowy ---")
    print("Otwórz w przeglądarce: http://localhost:5000")
    app.run(port=5000, debug=True)
