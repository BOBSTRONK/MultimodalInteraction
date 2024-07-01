from pynput.keyboard import Key, Listener
from pynput.mouse import Listener
from pynput import keyboard
import os

next_key = [keyboard.Key.space, keyboard.Key.enter, keyboard.Key.right, keyboard.Key.down, 'n']
previous_key = [keyboard.Key.delete, keyboard.Key.left, keyboard.Key.up, 'p']


def on_click(x, y, button, pressed):
    if pressed:
        print("Mouse clicked, go next slide")
        os.system('osascript -e \'display notification "switch to next slide" with title "mouse click"\'' )


def on_press(key):
    if key in next_key or (hasattr(key, 'char') and key.char in next_key):
        print(f"{key} pressed, go next slide")
    elif key in previous_key or (hasattr(key, 'char') and key.char in previous_key):
        print(f"{key} pressed, go previous slide")

key_listener = keyboard.Listener(on_press=on_press)
key_listener.start()

with Listener(on_click=on_click) as listener:
    listener.join()