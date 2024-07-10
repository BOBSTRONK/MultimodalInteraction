import os
import customtkinter as ctk

next_key = [
    "Return",
    "space",
    "Right",
    "Down",
    "n",
]

previous_key = [
    "BackSpace",
    "Left",
    "Up",
    "p",
]


def onKeyPress(event):
    if event.keysym in next_key:
        os.system(
            'osascript -e \'display notification "Switch to Next slide" with title "Key press"\''
        )
    elif event.keysym in previous_key:
        os.system(
            'osascript -e \'display notification "Switch to Previous slide" with title "Key press"\''
        )

def onMouseClick(event):
    if event.num == 1:  # Left click
        os.system(
            'osascript -e \'display notification "Switch to Next slide" with title "Mouse click"\''
        )
    elif event.num == 3:  # Right click
        os.system(
            'osascript -e \'display notification "Switch to Previous slide" with title "Mouse click"\''
        )

def process_presentation():
    
    # Process frames on the main thread
    root.bind('<KeyPress>', onKeyPress)
    root.bind('<Button>', onMouseClick) 

root = ctk.CTk()
root.geometry('300x200')

right_frame = ctk.CTkFrame(root, width=560, height=400)
right_frame.pack(side="right", fill="both", expand=True)

start_detection_button = ctk.CTkButton(
    right_frame,
    text="Start Detection",
    fg_color="white",
    text_color="black",
    font=("Helvetica", 18, "bold"),
    command=process_presentation,  # This ensures the key binding happens on button click
)
start_detection_button.pack(pady=20)

root.mainloop()
