import Models.click_keyPress_detection as click_keyPress_detection
import Models.gesture_detection as gesture_detection
import Models.voice_recognition as voice_recognition

import cv2
import time
import threading
import subprocess
import collections

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

"""
subprocess.run(["osascript", "-e", script_next])
time.sleep(2)
subprocess.run(["osascript", "-e", script_previous])
time.sleep(2)
subprocess.run(["osascript", "-e", script_next])
"""


def main():
    click_detector = click_keyPress_detection.ClickKeyPressDetector()
    voice_recognizer = voice_recognition.VoiceRecognizer()
    gesture_detector = gesture_detection.GestureRecognizer(use_gpu=False)

    frame_queue = collections.deque(
        maxlen=1
    )  # Use deque with maxlen to keep only the latest frame

    # Start listening for clicks in a separate thread
    threading.Thread(target=click_detector.start_listening, daemon=True).start()

    # Start listening for voice commands in a separate thread
    threading.Thread(target=voice_recognizer.microphone, daemon=True).start()

    def capture_frames():
        cap = cv2.VideoCapture(0)  # need to change 0 or 1
        while True:
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            frame_queue.append(frame)  # Add frame to deque

    #        cap.release()

    # Start frame capture in a separate thread
    threading.Thread(target=capture_frames, daemon=True).start()

    # cv2.namedWindow("frame", cv2.WINDOW_GUI_NORMAL)

    while True:
        # Process frames on the main thread
        if frame_queue:
            frame = frame_queue.pop()
            frame = gesture_detector.process_frame(frame, "next1", "previous1")
            # cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # priority
        detected_value = None
        if voice_recognizer.value:
            detected_value = voice_recognizer.value
            voice_recognizer.value = None
        elif click_detector.value:
            # detected_value = click_detector.value
            click_detector.value = None
        elif gesture_detector.value:
            detected_value = gesture_detector.value
            gesture_detector.value = None

        if detected_value == "previous":
            subprocess.run(["osascript", "-e", script_previous])
            print(detected_value)
        elif detected_value == "next":
            subprocess.run(["osascript", "-e", script_next])
            print(detected_value)

        time.sleep(0.01)  # Small sleep to prevent CPU overuse

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
