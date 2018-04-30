import spotipy
import spotipy.oauth2 as oauth2
import numpy as np
import json
import sys
import yaml
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib

limitOfTracksApiCanProcess = 50

conf = yaml.load(open('conf/application.yml'))
CLIENT_ID = conf['client']['id']
CLIENT_SECRET = conf['client']['secret']
#INSERT YOUR CREDENTIALS HERE
credentials = oauth2.SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
token = credentials.get_access_token()
sp = spotipy.Spotify(auth=token)

def prepareProperFormatOfUrl(listOfUrls):
	constantPartOfString = 'spotify:track:'
	formattedUrlArr = []
	for url in listOfUrls:
		if(url[-1:] == "\n"):
			formattedUrlArr.append(constantPartOfString + url.split('/')[4][:-1])
		else:
			formattedUrlArr.append(constantPartOfString + url.split('/')[4])
	return formattedUrlArr


def readUrlFromFileReturnTrackUrl(filename):
	featuresFromFile = []
	with open(filename) as f:
		line = f.readline()
		while line:
			featuresFromFile.append(line[:])
			line = f.readline()
	return prepareProperFormatOfUrl(featuresFromFile)


def getTracksFeatures(trackUrlArr):
	vectorOfFeatures = []
	#API can process only 50 tracks at once
	for i in range(0, (len(trackUrlArr)-1), limitOfTracksApiCanProcess):
		try:
			if ((i+limitOfTracksApiCanProcess-1) > (len(trackUrlArr) - 1)):
				#if there is less tracks left than 50
				features = sp.audio_features(trackUrlArr[i:(len(trackUrlArr))])
			else:
				features = sp.audio_features(trackUrlArr[i:(i+limitOfTracksApiCanProcess)])
		except:
			print("Spotipy bug")
			continue

		features = json.loads(json.dumps(features, indent=4))
		for singleTrack in features:
			try:
				energy = float(singleTrack['energy'])
				liveness = float(singleTrack['liveness'])
				tempo = float(singleTrack['tempo'])
				speechiness = float(singleTrack['speechiness'])
				acousticness = float(singleTrack['acousticness'])
				instrumentalness = float(singleTrack['instrumentalness'])
				danceability = float(singleTrack['danceability'])
				loudness = float(singleTrack['loudness'])
				valence = float(singleTrack['valence'])
				vectorOfFeatures.append((energy,liveness, tempo, speechiness, acousticness, instrumentalness, danceability, loudness, valence))
			except:
				vectorOfFeatures.append((0,0,0,0,0,0,0,0,0))
				print("Unknown error")
				continue
		print(len(vectorOfFeatures), i)
	return vectorOfFeatures

def predictFromFeatures(featuresArr):
	predictArr = []
	#import kernel from file
	clf = joblib.load('trainedClf.pkl')
	for element in featuresArr:
		element = np.array(element)
		element = element.reshape(1, -1)
		predictArr.append(np.asscalar(clf.predict(element)))
	#returns simple array of predicted labels
	return predictArr


def writePredictionsToFile(predictedTracks):
	writeToFile = open("predictedTracks", "w")
	writeToFile.write(str(predictedTracks))
	writeToFile.close()

def predict(arrOfTrackUrls):
	feat = getTracksFeatures(arrOfTrackUrls)
	predictedTracks = predictFromFeatures(feat)
	listOfUrlAndPrediction = []
	for url, prediction in zip(arrOfTrackUrls, predictedTracks):
		listOfUrlAndPrediction.append((url, prediction))
#		listOfUrlAndPrediction.append(("https://open.spotify.com/track/" + url.split(':')[2], prediction))
	return listOfUrlAndPrediction

if __name__ == "__main__":
	predict(prepareProperFormatOfUrl(sys.argv[1]))
	
