import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

# Load the train and test data from pickle files
train_data_dict = pickle.load(open("Gesture/train_data.pickle", "rb"))
test_data_dict = pickle.load(open("Gesture/test_data.pickle", "rb"))

# Convert the loaded data and labels to Numpy arrays for further processing
x_train = np.asarray(train_data_dict["data"])
y_train = np.asarray(train_data_dict["labels"])
x_test = np.asarray(test_data_dict["data"])
y_test = np.asarray(test_data_dict["labels"])

# Train the model using training data
model_RFC = RandomForestClassifier()
model_RFC.fit(x_train, y_train)

y_predict_RFC = model_RFC.predict(x_test)
score_RFC = accuracy_score(y_predict_RFC, y_test)
print("{}% of samples were classified correctly!".format(score_RFC * 100))

# SVC
mode_svm = SVC()
mode_svm.fit(x_train, y_train)

y_predict_svm = mode_svm.predict(x_test)
score_svm = accuracy_score(y_predict_svm, y_test)
print("{}% of samples were classified correctly!".format(score_svm * 100))

if score_RFC > score_svm:
    model = model_RFC
else:
    model = mode_svm
# Save the trained model to a file
with open("./Gesture/model.p", "wb") as f:
    pickle.dump({"model": model}, f)
