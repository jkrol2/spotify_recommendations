import spotipy
import spotipy.oauth2 as oauth2
import json
import time

def readFromFile(filename) :
	listOfLinks2 = []
	with open("playlistLinks") as f:
		line = f.readline()
		while line:
			listOfLinks2.append(line[:-1])
			line = f.readline()
	f.close()
	return listOfLinks2



#DO NOT TOUCH - DO NOT LOOK - PRIVATE KEY
credentials = oauth2.SpotifyClientCredentials(''    ,'')
token = credentials.get_access_token()
sp = spotipy.Spotify(auth=token)

#read from file where you specified your playlists
listOfLinks = readFromFile('playlistLinks')
#open file for writing results
WriteToFile = open("tracksFeatures", "w")
#dataLine describe if the line contains data (URL) or name of playlist (skip this line)
dataLine = False
for line in listOfLinks:

		if(dataLine == False):
			dataLine = True
			continue
		else:
			dataLine = False

		typeOfPlaylist = int(line[:1])
		username = line.split('/')[4]
		playlist_id = line.split('/')[6]
		playlistUri = 'spotify:user:spotify:playlist:' + playlist_id
		#get playlist
		results = sp.user_playlist(username, playlist_id, fields="tracks,next")
		totalNumberOfTracks = int(json.dumps(results['tracks']['total'], indent=4))
		#iterate trough tracks
		for trackNumber in range(0, totalNumberOfTracks):
			try:
				#get track
				trackUri = json.dumps(results['tracks']['items'][trackNumber]['track']['uri'], indent=4)[1:-1]
				#index error - over 100 tracks in playlist :/
			except IndexError:
				print("IndexError!!! Ignore! :-) ")
				continue
			features = sp.audio_features(trackUri)
			vectorOfFeatures = []

			energy = float(json.dumps(features[0]['energy']))
			liveness = float(json.dumps(features[0]['liveness']))
			tempo = float(json.dumps(features[0]['tempo']))
			speechiness = float(json.dumps(features[0]['speechiness']))
			acousticness = float(json.dumps(features[0]['acousticness']))
			instrumentalness = float(json.dumps(features[0]['instrumentalness']))
			danceability = float(json.dumps(features[0]['danceability']))
			loudness = float(json.dumps(features[0]['loudness']))
			valence = float(json.dumps(features[0]['valence']))

			vectorOfFeatures.append((playlistUri, typeOfPlaylist, energy, liveness, tempo, speechiness, acousticness, instrumentalness, instrumentalness, danceability, loudness, valence))
			file.write(str(vectorOfFeatures)[2:-2]+"\n")
		print()

WriteToFile.close()