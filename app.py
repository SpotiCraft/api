from flask import Flask, request, render_template_string, Response
import json
import spotipy
import requests
import base64

import string
import random

from config import *

app = Flask(__name__)

authorization = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

logins = {}

def generate_random_string():
    letters = string.hexdigits.lower()
    random_part = ''.join(random.choice(letters) for _ in range(8))
    random_string = f"{random_part[:4]}-{random_part[4:]}"
    return random_string

@app.route('/api/getlink', methods=['GET'])
def getlink():
    state = generate_random_string()
    scope = "user-read-playback-state,playlist-read-private,playlist-read-collaborative,app-remote-control,user-modify-playback-state, user-library-modify,user-library-read"
    
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope, state=state)
    auth_url = sp_oauth.get_authorize_url()
    
    resp = Response(json.dumps({"url": auth_url}), mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/api/callback', methods=['GET'])
def callback():
    state = request.args.get('state')
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return "Error: " + error
    
    token = requests.post("https://accounts.spotify.com/api/token", headers={"Authorization": f"Basic {authorization}"}, data={
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).json()

    logins[state] = {"access_token": token["access_token"], "refresh_token": token["refresh_token"]}

    return render_template_string("Login successful! Enter `/sc confirm {{ state }}` or just click the `I've logged in!` button in Minecraft chat to proceed!", state=state)

@app.route("/api/gettoken/<state>", methods=['GET'])
def gettoken(state):
    if state not in logins:
        return "Error: Invalid state"
    
    
    response = Response(json.dumps(logins[state]), mimetype='application/json')
    response.headers['Access-Control-Allow-Origin'] = '*'
    del logins[state]

    return response

if __name__ == "__main__":
    app.run(port=8000)
