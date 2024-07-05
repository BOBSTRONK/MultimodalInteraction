import os
import pickle
import time
import numpy as np
import mediapipe as mp
import cv2


class GestureRecognizer:
    # Load the model
    model_dict = pickle.load(open("./model.p", "rb"))
    model = model_dict["model"]

    # BaseOptions in mediapipe library
    # define some pre-trained base gesture from mediapipe
    BaseOptions = mp.tasks.BaseOptions
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
    VisionRunningMode = mp.tasks.vision.RunningMode

    # Global variable to store the gesture result
    gesture_result = "None"

    @staticmethod
    def update_gesture_result(
        result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int
    ):
        """
        Static method to update the gesture result based on the recognizer's output.
        This method is called by the gesture recognizer when a result is available.

        Parameters:
        - result: The result from the gesture recognizer containing detected gestures.
        - output_image: The output image from the recognizer (not used here).
        - timestamp_ms: The timestamp of the result.
        """
        # filter the gesture in the base model of mediapipe
        # if the gesture in the base model is detected, then means there is no gesture that we are interested.
        if result.gestures and result.gestures[0]:
            GestureRecognizer.gesture_result = result.gestures[0][0].category_name
        else:
            GestureRecognizer.gesture_result = "None"

    def __init__(self, use_gpu=False):
        self.value = None
        self.use_gpu = use_gpu
        # Set up MediaPipe for hand detection
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        # Configure MediaPipe Hands to use CPU or GPU
        self.hands = self.mp_hands.Hands(
            static_image_mode=True,
            min_detection_confidence=0.3,
            model_complexity=1 if use_gpu else 0,
        )
        # set the option for the gesture recognizer
        self.options = self.GestureRecognizerOptions(
            #  initializes the base options required for the gesture recognizer.
            #  It includes the path to the base model.
            base_options=self.BaseOptions(model_asset_path="./gesture_recognizer.task"),
            # process frames in real-time as they are captured from the video stream
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            # This parameter specifies a callback function that will be called whenever
            # a new result is available from the gesture recognizer.
            result_callback=GestureRecognizer.update_gesture_result,
        )

    # process a single video frame to detect and recognize hand gestures
    # frame: A single video frame (image) in BGR format
    def process_frame(
        self,
        frame,
        gestureToDetectForNext,
        gestureToDetectForPrevious,
    ):
        with self.GestureRecognizer.create_from_options(self.options) as recognizer:
            # store the recognizer instance in class
            self.recognizer = recognizer
            # initialize lists to store auxilary data and coordinates
            data_aux = []
            x_ = []
            y_ = []
            # Get the frame dimensions
            H, W, _ = frame.shape
            # convert Frame to rgb
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # process the frame using MediaPipe hands
            results = self.hands.process(frame_rgb)
            # check if hand landmarks are detected
            if results.multi_hand_landmarks:
                # iterate over each detected hand
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw the hand landmarks on the frame
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style(),
                    )
                    # separate landmarks for each hand
                    # Extract the landmarks into a list
                    hand_landmarks_list = [
                        hand_landmarks.landmark
                        for hand_landmarks in results.multi_hand_landmarks
                    ]
                    # iterate over each set of hand landmarks
                    for hand_landmarks in hand_landmarks_list:
                        # extract x and y coordinates of each landmark
                        # x and y are the points that has most significato
                        for i in range(len(hand_landmarks)):
                            x = hand_landmarks[i].x
                            y = hand_landmarks[i].y
                            # collect these coordinates into aux lists for further processing
                            x_.append(x)
                            y_.append(y)
                        # normalize the coordinates
                        for i in range(len(hand_landmarks)):
                            x = hand_landmarks[i].x
                            y = hand_landmarks[i].y
                            # Normalize the coordinates relative to the minimum x and y values
                            # because we need to convert double to int
                            # crucial because it makes the coordinates independent of their absolute position in the frame
                            # instead they are now relative to the hand's bounding box
                            # this means the gesture recognition model will focus on the shape
                            # and relative position of the landmarks rather than their absolute position with frame
                            data_aux.append(x - min(x_))
                            data_aux.append(y - min(y_))
                        # image coordinate system starts with origin (0,0) at top-left corner of the image frame
                        # different from cartesian coordinate system
                        # x-axis increases from left to right, y-axis increases from top to bottom
                        # Calculate the bounding box for the hand
                        x1 = int(min(x_) * W) - 10
                        y1 = int(min(y_) * H) - 10
                        x2 = int(max(x_) * W) - 10
                        y2 = int(max(y_) * H) - 10
                        # Predict the gesture using the pre-trained model
                        prediction = self.model.predict([np.asarray(data_aux)])
                        # stores the predicted gesture label
                        predicted_gesture = prediction[0]
                        # Draw the bounding box and the predicted gesture on the frame
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
                        # get current timestamp in milliseconds
                        timestamp_ms = int(time.time() * 1000)
                        # create a Mediapipe Image from rgb frame
                        mp_image = mp.Image(
                            image_format=mp.ImageFormat.SRGB, data=frame_rgb
                        )
                        # perform async gesture recognition
                        self.recognizer.recognize_async(mp_image, timestamp_ms)

                        if self.gesture_result == "None":
                            if (
                                # predicted_gesture == "next1"
                                # or predicted_gesture == "next2"
                                predicted_gesture
                                == gestureToDetectForNext
                            ):
                                self.value = "next"
                                os.system(
                                    'osascript -e \'display notification "Switch to Next slide" with title "Gesture recognition"\''
                                )
                                time.sleep(1)
                            elif (
                                # predicted_gesture == "previous1"
                                # or predicted_gesture == "previous2"
                                predicted_gesture
                                == gestureToDetectForPrevious
                            ):
                                os.system(
                                    'osascript -e \'display notification "Switch to Previous slide" with title "Gesture recognition"\''
                                )
                                self.value = "previous"
                                time.sleep(1)

                        x_ = []
                        y_ = []
                        data_aux = []

        return frame
