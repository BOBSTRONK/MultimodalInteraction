from pynput.keyboard import Key, Listener as KeyListener
from pynput.mouse import Listener as MouseListener
from pynput import keyboard
import os


# Class to detect ouse clicks and key presses
class ClickKeyPressDetector:
    # Define list of keys to move to the next and previous slides
    next_key = [
        keyboard.Key.space,
        keyboard.Key.enter,
        keyboard.Key.right,
        keyboard.Key.down,
        "n",
    ]
    previous_key = [keyboard.Key.delete, keyboard.Key.left, keyboard.Key.up, "p"]

    def __init__(self):
        # initialize the value to store the direction of slide change
        self.value = None

    # method to handle mouse click events
    def on_click(self, x, y, button, pressed):
        if pressed:
            # print("Mouse clicked, go next slide")
            # display the notification for moving to the next slide
            os.system(
                'osascript -e \'display notification "Switch to Next slide" with title "Mouse click"\''
            )
            self.value = "next"

    # Method to handle key press events
    def on_press(self, key):
        if key in self.next_key or (hasattr(key, "char") and key.char in self.next_key):
            # print(f"{key} pressed, go next slide")
            # if the key is in the next_key list, display a notification for moving to the next slide
            os.system(
                'osascript -e \'display notification "Switch to Next slide" with title "Key press"\''
            )
            self.value = "next"
        elif key in self.previous_key or (
            hasattr(key, "char") and key.char in self.previous_key
        ):
            # print(f"{key} pressed, go previous slide")
            # if the key is in the previous_key list, display a notification or moving to the previous slide
            os.system(
                'osascript -e \'display notification "Switch to Previous slide" with title "Key press"\''
            )
            self.value = "previous"

    def start_listening(self):
        # Create and start a Listener for key presses
        key_listener = KeyListener(on_press=self.on_press)
        key_listener.start()

        # Create and start a Listener for mouse clicks
        mouse_listener = MouseListener(on_click=self.on_click)
        mouse_listener.start()
        # Join the listerners to the main thread to keep the script running
        # ensuring that the event listeners remain active
        key_listener.join()
        mouse_listener.join()
