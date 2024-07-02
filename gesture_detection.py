import os
import pickle
import time
import numpy as np
import mediapipe as mp
import cv2

class GestureRecognizer:
    # load the model
    model_dict = pickle.load(open("./model.p", "rb"))
    model = model_dict["model"]

    def __init__(self, use_gpu=False):
        self.value = None
        self.use_gpu = use_gpu
        # set up mediapipe for hand detection
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        # Configure MediaPipe Hands to use CPU
        self.hands = self.mp_hands.Hands(
            static_image_mode=True,
            min_detection_confidence=0.3,
            model_complexity=0 if not self.use_gpu else 1
        )

    def process_frame(self, frame):
        data_aux = []
        x_ = []
        y_ = []

        H, W, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS, 
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style(),
                )

                hand_landmarks_list = [
                    hand_landmarks.landmark
                    for hand_landmarks in results.multi_hand_landmarks
                ]

                for hand_landmarks in hand_landmarks_list:
                    for i in range(len(hand_landmarks)):
                        x = hand_landmarks[i].x
                        y = hand_landmarks[i].y
                        x_.append(x)
                        y_.append(y)

                    for i in range(len(hand_landmarks)):
                        x = hand_landmarks[i].x
                        y = hand_landmarks[i].y
                        data_aux.append(x - min(x_))
                        data_aux.append(y - min(y_))

                    x1 = int(min(x_) * W) - 10
                    y1 = int(min(y_) * H) - 10
                    x2 = int(max(x_) * W) - 10
                    y2 = int(max(y_) * H) - 10

                    prediction = self.model.predict([np.asarray(data_aux)])
                    predicted_gesture = prediction[0]

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
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

                    if predicted_gesture == "next1" or predicted_gesture == "next2":
                        self.value = 'next'
                        os.system('osascript -e \'display notification "Switch to Next slide" with title "Gesture recognition"\'')
                        time.sleep(1)
                    elif predicted_gesture == "previous1" or predicted_gesture == "previous2":
                        os.system('osascript -e \'display notification "Switch to Previous slide" with title "Gesture recognition"\'')
                        self.value = 'previous'
                        time.sleep(1)

                    x_ = []
                    y_ = []
                    data_aux = []

        return frame
