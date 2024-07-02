import click_keyPress_detection
import gesture_detection
import voice_recognition

import cv2
import time
import threading
import collections

def main():
    click_detector = click_keyPress_detection.ClickKeyPressDetector()
    voice_recognizer = voice_recognition.VoiceRecognizer()
    gesture_detector = gesture_detection.GestureRecognizer(use_gpu=False)

    frame_queue = collections.deque(maxlen=1)  # Use deque with maxlen to keep only the latest frame

    # Start listening for clicks in a separate thread
    threading.Thread(target=click_detector.start_listening, daemon=True).start()

    # Start listening for voice commands in a separate thread
    threading.Thread(target=voice_recognizer.microphone, daemon=True).start()

    def capture_frames():
        cap = cv2.VideoCapture(1)  # need to change 0 or 1
        while True:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            frame_queue.append(frame)  # Add frame to deque
#        cap.release()

    # Start frame capture in a separate thread
    threading.Thread(target=capture_frames, daemon=True).start()

    #cv2.namedWindow("frame", cv2.WINDOW_GUI_NORMAL)

    while True:
        # Process frames on the main thread
        if frame_queue:
            frame = frame_queue.pop()
            frame = gesture_detector.process_frame(frame)
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        detected_value = None
        if voice_recognizer.value:
            detected_value = voice_recognizer.value
            voice_recognizer.value = None
        elif click_detector.value:
            detected_value = click_detector.value
            click_detector.value = None
        elif gesture_detector.value:
            detected_value = gesture_detector.value
            gesture_detector.value = None

        if detected_value: 
            # if detected_value == 'previous' do left
            print(detected_value)

        time.sleep(0.01)  # Small sleep to prevent CPU overuse

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
