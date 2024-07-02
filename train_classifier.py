import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

# Load the train and test data from pickle files
train_data_dict = pickle.load(open("train_data.pickle", "rb"))
test_data_dict = pickle.load(open("test_data.pickle", "rb"))

# Convert the loaded data and labels to Numpy arrays for further processing
x_train = np.asarray(train_data_dict["data"])
y_train = np.asarray(train_data_dict["labels"])
x_test = np.asarray(test_data_dict["data"])
y_test = np.asarray(test_data_dict["labels"])

# Train the model using training data
model = RandomForestClassifier()
model.fit(x_train, y_train)

# Use trained model to make predictions on the testing data
y_predict = model.predict(x_test)

# Calculate accuracy of the model predictions
score = accuracy_score(y_predict, y_test)
print("{}% of samples were classified correctly!".format(score * 100))

# Save the trained model to a file
with open("model.p", "wb") as f:
    pickle.dump({"model": model}, f)
