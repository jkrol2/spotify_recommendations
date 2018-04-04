import spotipy
import spotipy.oauth2 as oauth2
import json
import time

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

#DO NOT TOUCH - DO NOT LOOK - PRIVATE KEY
credentials = oauth2.SpotifyClientCredentials('1c9d265388fc4ed6890b6eccbc080ce9', '927b472f0d4a420fa93bcb8bf6ecc394')
token = credentials.get_access_token()
sp = spotipy.Spotify(auth=token)

listOfLinks = readFromFile('PlaylistToPredict')

WriteToFile = open("featuresOfTracksToPredict", "w")

limitOfTracksApiCanProcess = 50
i = 1
for linkToPlaylist in listOfLinks:
	start = time.time()
	typeOfPlaylist = int(linkToPlaylist[:1])
	username = linkToPlaylist.split('/')[4]
	playlist_id = linkToPlaylist.split('/')[6]
	#playlistUri = 'spotify:user:spotify:playlist:' + playlist_id
	try:
		tracks = get_playlist_tracks(username, playlist_id)
	except:
		print("End of file")
		continue

	for i in range(0,(len(tracks)-1), limitOfTracksApiCanProcess):

		if ((i+limitOfTracksApiCanProcess-1) > (len(tracks) - 1)):
			features = sp.audio_features(tracks[i:(len(tracks)-1)])
		else:
			features = sp.audio_features(tracks[i:(i+limitOfTracksApiCanProcess-1)])

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