import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib

def readFromFile(filename) :
	featuresFromFile = []
	with open(filename) as f:
		line = f.readline()
		while line:
			featuresFromFile.append(line[:-1])
			line = f.readline()
	return featuresFromFile

featuresFromFile = readFromFile('trackFeatures')

pX = []
py = []

#prepare arrays
for line in featuresFromFile:
	tmpArr = line.split(',')
	pX.append([tmpArr[2],
	 tmpArr[3],
	 tmpArr[4],
	 tmpArr[5],
	 tmpArr[6],
	 tmpArr[7],
	 tmpArr[8],
	 tmpArr[9],
	 tmpArr[10]])

	py.append(tmpArr[1])

pX = np.asarray(pX)
py = np.asarray(py)

#split data to train and test arrays
X_train, X_test, y_train, y_test = train_test_split(pX, py, test_size=0.33, random_state=42)

#create svm
clf = svm.SVC(kernel='linear', C = 1.0)

#train svm
clf.fit(X_train,y_train)

#export kernel
joblib.dump(clf, 'trainedClf.pkl')

X_test = np.asarray(X_test)
y_test = np.asarray(y_test)

#Types of tracks: 0 - sad 1 - happy 2 - party 3 - angry 4 - calm 5 - none
correct = 0
for i in range(0, len(y_test)):
	tempZ = np.array(X_test[i])
	tempZ = tempZ.reshape(1, -1)
	prediction = int(clf.predict(tempZ))
	actualValue = int(y_test[i])
	#assume that happy/party, angry/party, calm/sad and every 'none' track is treated as correct prediction
	if(prediction == actualValue):
		correct += 1
	elif ((prediction == 1 and actualValue == 2) or (prediction == 2 and actualValue == 1)):
		#happy/party
		correct +=1
	elif ((prediction == 3 and actualValue == 2) or (prediction == 2 and actualValue == 3)):
		#party/angry
		correct +=1
	elif ((prediction == 4 and actualValue == 0) or (prediction == 0 and actualValue == 4)):
		#calm/sad
		correct +=1
	elif(prediction == 5 or actualValue == 5):
		#every "none"
		correct +=1
	else:
		print(str(prediction) + " should be: " + str(y_test[i]))


print(correct)
print(len(y_test))
quality = correct/float(len(y_test))

print(quality)