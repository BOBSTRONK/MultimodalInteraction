import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import pickle
import subprocess
import time  # Import the time module
from pptx import Presentation
import os

# load the model
model_dict = pickle.load(open("./model.p", "rb"))
model = model_dict["model"]

presentationPath = "/Users/weidongcai/Documents/Big_Data_Presentation_CAI_1836167.pptx"

print(presentationPath)
# AppleScript commands to control PowerPoint
script = f"""
tell application "Microsoft PowerPoint"
    activate
    open "{presentationPath}"
    set slideShowSettings to slide show settings of active presentation
    set starting slide of slideShowSettings to 4
    set ending slide of slideShowSettings to 4
    run slide show slideShowSettings
end tell
"""

subprocess.run(["osascript", "-e", script])


# Move to the next slide
script_next = """
tell application "Microsoft PowerPoint"
	go to next slide slide show view of slide show window 1
end tell
"""

script_previous = """
tell application "Microsoft PowerPoint"
	go to previous slide slide show view of slide show window 1
end tell
"""
subprocess.run(["osascript", "-e", script_next])
time.sleep(2)
subprocess.run(["osascript", "-e", script_previous])
time.sleep(2)
subprocess.run(["osascript", "-e", script_next])


# Define keyboard shortcuts for controlling the presentation
NEXT_SLIDE_KEY = "right"  # Change as needed
PREVIOUS_SLIDE_KEY = "left"  # Change as needed

# start the video capture
cap = cv2.VideoCapture(0)
# set up mediapipe for hand detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# go to a specific slide numer = press a number + enter

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
while True:
    # lists to store processed hand landmark data and their x and y coordinates
    data_aux = []
    x_ = []
    y_ = []

    # capture frame from webcam
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    # dimension of the frame
    H, W, _ = frame.shape
    # convert the frame from BGR to RGB for mediapipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Processes the RGB frame to detect handmarks
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # draw the landmarks on the frame
            mp_drawing.draw_landmarks(
                frame,  # image to draw
                hand_landmarks,  # model output
                mp_hands.HAND_CONNECTIONS,  # hand connections
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style(),
            )

        # Separate landmarks for each hand
        # extracts the list of landmarks for each detected hand
        hand_landmarks_list = [
            hand_landmarks.landmark for hand_landmarks in results.multi_hand_landmarks
        ]

        for hand_landmarks in hand_landmarks_list:
            for i in range(len(hand_landmarks)):
                # normalized coordinates of each landmark
                x = hand_landmarks[i].x
                y = hand_landmarks[i].y
                # collects these coordinates into lists for futher processing
                x_.append(x)
                y_.append(y)

            for i in range(len(hand_landmarks)):
                x = hand_landmarks[i].x
                y = hand_landmarks[i].y
                # normalize the coordinates relative to the minimum x and y values
                # because we need to convert double to int
                # crucial because it makes the coordinates independent of their absolute position in frame
                # instead they are now relative to the hand's bounding box
                # this means the gesture recognition model will focus on the shape
                # and relative positions of the landmarks rather than their absolute position with frame
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

            # image coordinate system starts with origin (0,0) at top-left corner of the image frame
            # different from cartesian coordinate system
            # x-axis increases from left to right, y axis increases from top to bottom
            # calculate bounding box coordinates for the Hand
            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10

            x2 = int(max(x_) * W) - 10
            y2 = int(max(y_) * H) - 10

            # predict the gesture based on the normalized landmark data
            prediction = model.predict([np.asarray(data_aux)])
            # Stores the predicted gesture label
            predicted_gesture = prediction[0]

            # Draws a bounding box around the hand
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            # Display the predicted gesture on the frame
            cv2.putText(
                frame,
                predicted_gesture,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.3,
                (0, 0, 0),
                3,
                cv2.LINE_AA,
            )

            # Control PowerPoint slides based on detected gestures
            if predicted_gesture == "next1" or predicted_gesture == "next2":
                pyautogui.press(NEXT_SLIDE_KEY)
                time.sleep(0.5)  # Add a delay of 1 second
            elif predicted_gesture == "previous1" or predicted_gesture == "previous2":
                pyautogui.press(PREVIOUS_SLIDE_KEY)
                time.sleep(0.5)  # Add a delay of 1 second

            # Reset lists for the next hand
            x_ = []
            y_ = []
            data_aux = []

    cv2.imshow("frame", frame)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
