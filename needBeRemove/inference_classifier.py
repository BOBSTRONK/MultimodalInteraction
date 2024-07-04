import cv2
import pickle
import time
import numpy as np
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Global variable to store the gesture result
gesture_result = "None"

# Define a callback function to handle the results
def update_gesture_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global gesture_result
    if result.gestures and result.gestures[0]:
        gesture_result = result.gestures[0][0].category_name
    else:
        gesture_result = "None"

# Create gesture recognizer options
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='./gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=update_gesture_result
)

'''
# Initialize the gesture recognizer
with GestureRecognizer.create_from_options(options) as recognizer:
    # Initialize the video capture
    cap = cv2.VideoCapture(1)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        H, W, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get the current time in milliseconds
        timestamp_ms = int(time.time() * 1000)

        # Process the frame with the gesture recognizer
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        recognizer.recognize_async(mp_image, timestamp_ms)

        # Draw the gesture result on the frame
        cv2.putText(frame, f'Gesture: {gesture_result}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        cv2.imshow('Gesture Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
'''

model_dict = pickle.load(open("./model.p", "rb"))
model = model_dict["model"]  # extract the trained model
# initialize the video capture from default webcam
cap = cv2.VideoCapture(1)

# initialize Mediapipe's hands solution
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# create a hands object with specific settings
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Dictionary to map model prediction to actual charaters
#labels_dict = {0: "A", 1: "B", 2: "L"}  # need to change

while True:
    with GestureRecognizer.create_from_options(options) as recognizer:

        # Auxiliary (辅助) lists to store landmark positions and processed data
        data_aux = []
        x_ = []
        y_ = []

        # read a frame from the webcam
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        # get frame dimensions
        H, W, _ = frame.shape
        # convert the frame to RGB color space for mediapipe processing
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Process the frame to detect hand landmarks
        results = hands.process(frame_rgb)
        # check if any hands are detected in the frame
        if results.multi_hand_landmarks:
            # Loop over each detected hand
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks and connections on the original frame
                mp_drawing.draw_landmarks(
                    frame,  # image to draw
                    hand_landmarks,  # model output
                    mp_hands.HAND_CONNECTIONS,  # hand connections
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style(),
                )

            # Separate landmarks for each hand
            hand_landmarks_list = [
                hand_landmarks.landmark for hand_landmarks in results.multi_hand_landmarks
            ]
            # Loop over each detected hand's landmarks
            for hand_landmarks in hand_landmarks_list:
                for i in range(len(hand_landmarks)):
                    # extract landmark coordinates (x,y)
                    x = hand_landmarks[i].x
                    y = hand_landmarks[i].y

                    x_.append(x)
                    y_.append(y)

                for i in range(len(hand_landmarks)):
                    # normalize the coordinates relative to the minimum x and y values
                    # because we need to convert double to int
                    x = hand_landmarks[i].x
                    y = hand_landmarks[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))
                # calculate bounding box coordinates for the Hand
                x1 = int(min(x_) * W) - 10
                y1 = int(min(y_) * H) - 10

                x2 = int(max(x_) * W) - 10
                y2 = int(max(y_) * H) - 10

                # Get the current time in milliseconds
                timestamp_ms = int(time.time() * 1000)

                print(f'Gesture: {gesture_result}')

                # Process the frame with the gesture recognizer
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
                recognizer.recognize_async(mp_image, timestamp_ms)

                if gesture_result == 'None':
                # Predict the character/gesture using the trained model
                    prediction = model.predict([np.asarray(data_aux)])
                    # Map prediction to character
                    # predicted_character = labels_dict[int(prediction[0])]
                    predicted_character = prediction[0]
                    #print(prediction)
                    # draw a rectangle around the detected hand
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
                    # put the predicted character above the rectangle
                    cv2.putText(
                        frame,
                        predicted_character,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.3,
                        (0, 0, 0),
                        3,
                        cv2.LINE_AA,
                    )

                # Reset lists for the next hand
                x_ = []
                y_ = []
                data_aux = []

        cv2.imshow("frame", frame)
        cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()