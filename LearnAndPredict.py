import numpy as np
from sklearn import svm

def readFromFile(filename) :
	featuresFromFile = []
	with open(filename) as f:
		line = f.readline()
		while line:
			featuresFromFile.append(line[:-1])
			line = f.readline()
	f.close()
	return featuresFromFile

featuresFromFile = readFromFile('featuresOfTracksToLearn')

X = []
y = []

for line in featuresFromFile:
	tmpArr = line.split(',')
	X.append([tmpArr[2],
	 tmpArr[3],
	 tmpArr[4],
	 tmpArr[5],
	 tmpArr[6],
	 tmpArr[7],
	 tmpArr[8],
	 tmpArr[9],
	 tmpArr[10]])

	y.append(tmpArr[1])

X = np.asarray(X)
y = np.asarray(y)

clf = svm.SVC(kernel='linear', C = 1.0)

clf.fit(X,y)

featuresToPredict = readFromFile('featuresOfTracksToPredict')

Z = []
y2 = []

for line in featuresToPredict:
	tmpArr = line.split(',')
	Z.append([tmpArr[2],
	 tmpArr[3],
	 tmpArr[4],
	 tmpArr[5],
	 tmpArr[6],
	 tmpArr[7],
	 tmpArr[8],
	 tmpArr[9],
	 tmpArr[10]])

	y2.append(tmpArr[1])

Z = np.asarray(Z)
y2 = np.asarray(y2)

correct = 0
for i in range(0, len(y2)):
	tempZ = np.array(Z[i])
	tempZ = tempZ.reshape(1, -1)
	prediction = int(clf.predict(tempZ))

	if(prediction != int(y2[i])):
		print(str(prediction) + " should be: " + str(y2[i]))
	else:
		correct += 1


print(correct)
print(len(y2))
quality = correct/float(len(y2))

print(quality)
