import json
import requests
import base64
import urllib
import yaml
from flask import Flask, request, redirect, g, render_template
import spotipy

conf = yaml.load(open('conf/application.yml'))
CLIENT_ID = conf['client']['id']
CLIENT_SECRET = conf['client']['secret']


app = Flask(__name__)

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

AUTH_HEADER = []

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}

@app.route("/")
def main():
    return 'ok'

@app.route("/login")
def login():
    url_args = "&".join(["{}={}".format(key, urllib.quote(val))
                         for key, val in auth_query_parameters.iteritems()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route("/moodify")
def get_playlist(): 
    req =  requests.get("https://api.spotify.com/v1/me", headers=AUTH_HEADER[0])
    return req.text 
 
@app.route("/callback/q")
def callback():
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    AUTH_HEADER.append(authorization_header)
    
    req =  requests.get("https://api.spotify.com/v1/me", headers=authorization_header)
    return req.text 
#    return redirect("/moodify")

app.run(host='0.0.0.0',port=PORT)
