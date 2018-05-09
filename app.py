import json
import requests
import base64
import urllib
import yaml
import random
from flask import Flask, request, redirect, g, render_template, Response, url_for
import spotipy
import justPredict

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
SCOPE = "playlist-modify-public playlist-modify-private user-top-read user-read-recently-played user-library-read user-follow-read"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}

@app.route("/", methods=["GET","POST"])
def main():
    if request.method == 'POST':
        global mood
        mood = request.form['mood']
#        return redirect(url_for('.login', mood=mood))
        return redirect('/login')
    return render_template('index.html')

@app.route("/login")
def login():
    url_args = "&".join(["{}={}".format(key, urllib.quote(val))
                         for key, val in auth_query_parameters.iteritems()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

def get_songs_from_saved_tracks(songs, authorization_header):
    for offset in xrange(100):
        req = requests.get('https://api.spotify.com/v1/me/tracks?offset='+str(50*offset)+'&limit=50', headers=authorization_header)
        if req.json()['next'] == None:
            print("offset: ", offset)
            break
        for track in req.json()['items']:
            songs.append(track['track']['external_urls']['spotify'])


def get_songs_from_saved_artists(songs, authorization_header):
    req =  requests.get("https://api.spotify.com/v1/me/following?type=artist", headers=authorization_header)
    artists_ids = [a_id['id'] for a_id in req.json()['artists']['items']]
    for artist in artists_ids:
        res = requests.get("https://api.spotify.com/v1/artists/"+artist+"/top-tracks?country=PL&limit=50", headers=authorization_header)
        for track in res.json()['tracks']:
            songs.append(track['external_urls']['spotify'])

def create_playlist(moodified_songs, authorization_header):
    req = requests.get("https://api.spotify.com/v1/me/", headers=authorization_header)
    user_id = str(req.json()['id'])
    
    req = requests.get("https://api.spotify.com/v1/users/{user_id}/playlists".format(user_id=user_id), headers=authorization_header)
    for playlist in req.json()['items']:
        if playlist['name'] == 'Moodify playlist':
            playlist_id = playlist['id']
            playlist_uri = playlist['uri']
            break
    else:
        payload = {"name" : "Moodify playlist"}
        req = requests.post("https://api.spotify.com/v1/users/{0}/playlists".format(user_id), json=payload, headers=authorization_header)
        playlist_id = str(req.json()['id'])
        playlist_uri = str(req.json()['uri'])

    payload = {"uris": ["spotify:track:"+str(track.split('track/')[1]) for track in moodified_songs]}
    req = requests.put("https://api.spotify.com/v1/users/{user_id}/playlists/{playlist_id}/tracks".format(user_id=user_id, playlist_id=playlist_id), headers=authorization_header, json=payload)

    return playlist_uri
     

@app.route("/callback/q")
def callback():
    #mood = 4 #print "mood: ", mood
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
    songs = []
    
    get_songs_from_saved_tracks(songs, authorization_header)
    get_songs_from_saved_artists(songs, authorization_header)
    moodified_songs = []
    for x in xrange(0, len(songs), 50):
        if len(moodified_songs) == 20:
            break
        for song in justPredict.predict(songs[x:x+50]):
            if int(song[1]) == int(mood):
                moodified_songs.append(song[0])
    if len(moodified_songs) < 5:
        return render_template('tonie.html')

    if len(moodified_songs < 20:
        chosen_songs = moodified_songs
    else:
        chosen_songs = []
        while len(chosen_songs) < 20:
            chosen_songs.append(random.choice(moodified_songs))
        
    return render_template('return.html', moodif=str(create_playlist(chosen_songs, authorization_header)))
    return redirect('/return')
    #return render_template('moodify.html')

app.run(host='0.0.0.0',port=PORT)
