import spotipy
import spotipy.oauth2 as oauth2
import json
import time
import yaml

def readFromFile(filename) :
	listOfLinks2 = []
	dataLine = False
	with open(filename) as f:
		line = f.readline()
		while line:
			if(dataLine == True):
				listOfLinks2.append(line[:-1])
			dataLine = not dataLine
			line = f.readline()
	f.close()
	return listOfLinks2

def get_playlist_tracks(username,playlist_id):
	results = sp.user_playlist_tracks(username,playlist_id)
	tracks = results['items']
	while results['next']:
		results = sp.next(results)
		tracks.extend(results['items'])
	trackUriList = []
	for tr in tracks:
		trackUriList.append(tr['track']['uri'])
	return trackUriList


conf = yaml.load(open('conf/application.yml'))
CLIENT_ID = conf['client']['id']
CLIENT_SECRET = conf['client']['secret']
print(CLIENT_ID)
print(CLIENT_SECRET)
#INSERT YOUR CREDENTIALS HERE
credentials = oauth2.SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
token = credentials.get_access_token()
sp = spotipy.Spotify(auth=token)

listOfLinks = readFromFile('playlistLinks')

WriteToFile = open("trackFeatures", "w")

limitOfTracksApiCanProcess = 50
i = 1
for linkToPlaylist in listOfLinks:
	start = time.time()
	typeOfPlaylist = int(linkToPlaylist[:1])
	username = linkToPlaylist.split('/')[4]
	playlist_id = linkToPlaylist.split('/')[6]
	#playlistUri = 'spotify:user:spotify:playlist:' + playlist_id
	try:
		#every line except the last one has '\n' char at the end
		tracks = get_playlist_tracks(username, playlist_id[:-1])
	except:
		try:
			#it goes here only in the last line
			tracks = get_playlist_tracks(username, playlist_id)
		except:
			print("End of file")
			continue

	#API can process only 50 tracks at once
	for i in range(0,(len(tracks)-1), limitOfTracksApiCanProcess):
		try:
			if ((i+limitOfTracksApiCanProcess-1) > (len(tracks) - 1)):
				features = sp.audio_features(tracks[i:(len(tracks))])
			else:
				features = sp.audio_features(tracks[i:(i+limitOfTracksApiCanProcess)])
		except:
			print("Spotipy bug")
			continue

		features = json.loads(json.dumps(features, indent=4))
		for singleTrack in features:
			try:
				vectorOfFeatures = []
				energy = float(singleTrack['energy'])
				liveness = float(singleTrack['liveness'])
				tempo = float(singleTrack['tempo'])
				speechiness = float(singleTrack['speechiness'])
				acousticness = float(singleTrack['acousticness'])
				instrumentalness = float(singleTrack['instrumentalness'])
				danceability = float(singleTrack['danceability'])
				loudness = float(singleTrack['loudness'])
				valence = float(singleTrack['valence'])
				vectorOfFeatures.append((linkToPlaylist, typeOfPlaylist, energy,liveness,
				 tempo, speechiness, acousticness, instrumentalness, danceability, loudness, valence))
				WriteToFile.write(str(vectorOfFeatures)[2:-2]+"\n")
			except:
				print("Unknown error")
				continue

	end = time.time()
	print(i, end - start)
	i = i +1
WriteToFile.close()