import cv2
import pickle
import numpy as np
import mediapipe as mp

model_dict = pickle.load(open("./model.p", "rb"))
model = model_dict["model"]  # extract the trained model
# initialize the video capture from default webcam
cap = cv2.VideoCapture(0)

# initialize Mediapipe's hands solution
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# create a hands object with specific settings
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Dictionary to map model prediction to actual charaters
labels_dict = {0: "A", 1: "B", 2: "L"}  # need to change

while True:
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

            # Predict the character/gesture using the trained model
            prediction = model.predict([np.asarray(data_aux)])
            # Map prediction to character
            # predicted_character = labels_dict[int(prediction[0])]
            predicted_character = prediction[0]
            print(prediction)
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
