import os
import cv2

# A script for collecting image data

DATA_DIR = "./data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# different categories for the gestures
classes = ["next1", "next2", "previous1", "previous2", "none"]
# number of images to capture for each gesture
dataset_size = 50
# number of different gestures to capture per class
gestures_per_class = 2

# initializes the webcam for video capture
# 0 refers the default webcam of the system
cap = cv2.VideoCapture(0)

# check directory of classes exists or not, if not, create the directory
for class_label in classes:
    if not os.path.exists(os.path.join(DATA_DIR, class_label)):
        os.makedirs(os.path.join(DATA_DIR, class_label))

    print("Collecting data for class {}".format(class_label))

    for gesture_count in range(gestures_per_class):
        while True:
            # captures a frame from the webcam
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)  # avoid mirroring
            # adds text to the frame to prompt the user the information
            cv2.putText(
                frame,
                f'Ready? Press "S" to Start. Collecting gesture {gesture_count + 1} for class {class_label}',
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            # display the frame with the prompt in a window
            cv2.imshow("frame", frame)
            # wait for a key press for 1 millisecond
            key = cv2.waitKey(1)
            # "s" is pressed, the loop breaks, and script proceeds to capture images
            if key == ord("s"):
                break
            elif key == ord("q"):
                cap.release()
                cv2.destroyAllWindows()
                exit()

        print(f"Collecting gesture {gesture_count + 1} for class {class_label}")

        counter = 0
        while counter < dataset_size:
            # captures a frame from the webcam
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            cv2.imshow("frame", frame)
            cv2.waitKey(25)
            # saves the captured frame as Jpeg file
            cv2.imwrite(
                os.path.join(DATA_DIR, class_label, f"{gesture_count}_{counter}.jpg"),
                frame,
            )
            counter += 1

cap.release()
cv2.destroyAllWindows()
