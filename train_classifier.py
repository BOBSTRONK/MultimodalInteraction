import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np


data_dict = pickle.load(open("./data.pickle", "rb"))
# convert the loaded data and labels to Numpy arrays for further processing
# data is input features
data = np.asarray(data_dict["data"])
# target label
labels = np.asarray(data_dict["labels"])
# Split the dataset into train, testing sets
# 20% of data is reserved for testing
# shuffle the data before splliting
# stratify = labels: mantain the label distribution in both training and testing sets
x_train, x_test, y_train, y_test = train_test_split(
    data, labels, test_size=0.2, shuffle=True, stratify=labels
)

model = RandomForestClassifier()
# training the model using training data
model.fit(x_train, y_train)
# use trainned model to make predictions on the testing data
y_predict = model.predict(x_test)
# calculate accuracy of the model predictions
score = accuracy_score(y_predict, y_test)

print("{}% of samples were classified correctly !".format(score * 100))

f = open("model.p", "wb")
pickle.dump({"model": model}, f)
f.close()
