from flask import Flask

app = Flask(__name__)

@app.route("/")
def main():
    return 'pick your mood'

@app.route("/<mood>")
def get_playlist(mood):
    return mood


@app.route("/login")
def login_to_spotify():
    return 'logged in'

app.run()
