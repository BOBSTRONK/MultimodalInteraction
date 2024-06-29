import os
import cv2
import pickle

import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt

# provides the hand detection and tracking
mp_hands = mp.solutions.hands
# drwaing annotations on images (draw landmarks)
mp_drawing = mp.solutions.drawing_utils
# styles for drwaing
mp_drawing_styles = mp.solutions.drawing_styles
# initialize the hand detection and tracking pipeline
# static_image_mode to treat input like a image rather than a video stream;
# in static_image_mode each frame will be processed independently, 提高accuracy when there are significant variations between frames
# min_detection_confidence=0.3, 0.3 means that the model will be more 宽容, higher chance of false positive
# higher min_detection_confidence would make the model stricter, reducing chance of false detections, but possibly missing some hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# create directory for data saving
DATA_DIR = "./data"

# data will be produce to make the classification
data = []
# categorie for each one of the images / datapoint
labels = []

# iterate all the image in the directory
for dir_ in os.listdir(DATA_DIR):
    if dir_.startswith("."):
        continue

    for img_path in os.listdir(os.path.join(DATA_DIR, dir_)):
        if img_path.startswith("."):
            continue
        data_aux = []

        # save x horizontal and y vertical coordinates of all landmarks
        x_ = []
        y_ = []

        # Load the image
        img = cv2.imread(os.path.join(DATA_DIR, dir_, img_path))

        # Check if the image is loaded successfully
        if img is None:
            print("Failed to load image:", img_path)
            continue

        # convert image into RGB to then feed it into the mediapipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # detect all the landmarks in the image
        results = hands.process(img_rgb)
        if results.multi_hand_landmarks:
            # create an array for all the landmarks that detect
            for hand_landmarks in results.multi_hand_landmarks:
                # iterate the hand landmarks through the array of hands
                # each hand is represented as a list of 21 hand landmarks
                for i in range(len(hand_landmarks.landmark)):
                    # x,y are normalized to [0.0, 1.0] by the image width and height respectively
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    # these array of landmark will represent our image
                    x_.append(x)
                    y_.append(y)

                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))

            data.append(data_aux)
            # each directory will contain a sample, the smaple will be coded in name of directory
            labels.append(dir_)

# Check if all the lengths of data_aux are consistent
data_lengths = [len(item) for item in data]
print("Unique lengths of data_aux:", set(data_lengths))

# Convert data and labels to numpy arrays
data = np.array(data)
labels = np.array(labels)

# Save data and labels using pickle
with open("data.pickle", "wb") as f:
    print("Saving data to data.pickle")
    pickle.dump({"data": data, "labels": labels}, f)
