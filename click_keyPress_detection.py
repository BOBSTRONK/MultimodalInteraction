from pynput.keyboard import Key, Listener as KeyListener
from pynput.mouse import Listener as MouseListener
from pynput import keyboard
import os

class ClickKeyPressDetector:
    next_key = [keyboard.Key.space, keyboard.Key.enter, keyboard.Key.right, keyboard.Key.down, 'n']
    previous_key = [keyboard.Key.delete, keyboard.Key.left, keyboard.Key.up, 'p']

    def __init__(self):
        self.value = None

    def on_click(self, x, y, button, pressed):
        if pressed:
            #print("Mouse clicked, go next slide")
            os.system('osascript -e \'display notification "Switch to Next slide" with title "Mouse click"\'')
            self.value = 'next'

    def on_press(self, key):
        if key in self.next_key or (hasattr(key, 'char') and key.char in self.next_key):
            #print(f"{key} pressed, go next slide")
            os.system('osascript -e \'display notification "Switch to Next slide" with title "Key press"\'')
            self.value = 'next'
        elif key in self.previous_key or (hasattr(key, 'char') and key.char in self.previous_key):
            #print(f"{key} pressed, go previous slide")
            os.system('osascript -e \'display notification "Switch to Previous slide" with title "Key press"\'')
            self.value = 'previous'

    def start_listening(self):
        key_listener = KeyListener(on_press=self.on_press)
        key_listener.start()

        mouse_listener = MouseListener(on_click=self.on_click)
        mouse_listener.start()

        key_listener.join()
        mouse_listener.join()