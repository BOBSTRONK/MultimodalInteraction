import os
import cv2
import pickle
import numpy as np
import mediapipe as mp

# Provides the hand detection and tracking
mp_hands = mp.solutions.hands
# Drawing annotations on images (draw landmarks)
mp_drawing = mp.solutions.drawing_utils
# Styles for drawing
mp_drawing_styles = mp.solutions.drawing_styles

# Initialize the hand detection and tracking pipeline
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Directory for data saving
DATA_DIR = "./data"

# Create lists for data and labels
train_data = []
train_labels = []
test_data = []
test_labels = []

# Specify the persons for training and testing
train_persons = ["elena1", "elena2", "varma", "cai_cropped", 
                 "valerio_cropped", "valentino_cropped", "carlo_cropped", "alba"] 
test_persons = ["daniele", "emanuele", "stefano"]

# Iterate all the images in the directory
for dir_ in os.listdir(DATA_DIR):
    if dir_.startswith("."):
        continue
    person_dir = os.path.join(DATA_DIR, dir_)
    if not os.path.isdir(person_dir):
        continue

    for img_dir in os.listdir(person_dir):
        if img_dir.startswith("."):
            continue
        gesture_dir = os.path.join(person_dir, img_dir)

        for img_path in os.listdir(gesture_dir):
            if img_path.startswith("."):
                continue

            img_full_path = os.path.join(gesture_dir, img_path)
            img = cv2.imread(img_full_path)

            # Check if the image is loaded successfully
            if img is None:
                print("Failed to load image:", img_path)
                continue

            data_aux = []
            # Save x horizontal and y vertical coordinates of all landmarks
            x_ = []
            y_ = []

            # Convert image into RGB to then feed it into the mediapipe
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Detect all the landmarks in the image
            results = hands.process(img_rgb)
            if results.multi_hand_landmarks:
                # Create an array for all the landmarks that detect
                for hand_landmarks in results.multi_hand_landmarks:
                # Iterate the hand landmarks through the array of hands
                    for i in range(len(hand_landmarks.landmark)):
                        # x,y are normalized to [0.0, 1.0] by the image width and height respectively
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        # These array of landmark will represent our image
                        x_.append(x)
                        y_.append(y)

                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        data_aux.append(x - min(x_))
                        data_aux.append(y - min(y_))

                if dir_ in train_persons:
                    train_data.append(data_aux)
                    train_labels.append(img_dir)
                elif dir_ in test_persons:
                    test_data.append(data_aux)
                    test_labels.append(img_dir)
            else:
                print(f"No hand landmarks detected in image: {img_full_path}")

# Convert data and labels to numpy arrays
train_data = np.array(train_data)
train_labels = np.array(train_labels)
test_data = np.array(test_data)
test_labels = np.array(test_labels)

# Save train and test data using pickle
with open("./Gesture/train_data.pickle", "wb") as f:
    print("Saving train data to train_data.pickle")
    pickle.dump({"data": train_data, "labels": train_labels}, f)

with open("./Gesture/test_data.pickle", "wb") as f:
    print("Saving test data to test_data.pickle")
    pickle.dump({"data": test_data, "labels": test_labels}, f)
