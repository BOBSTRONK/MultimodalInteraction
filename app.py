# root = tk.Tk()
# root.title("MPPTC")

# app_description = tk.Label(root, text="Multimodal PPT controller")
# app_description.pack()
# open_button = tk.Button(root, text="Open PowerPoint", command=open_file_dialog)
# open_button.pack(padx=20, pady=20)
# selected_file_label = tk.Label(root, text="No PowerPoint is selected:")

# selected_file_label.pack()
# root.mainloop()

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
from PIL import Image, ImageTk


# AppleScript commands to control PowerPoint
def open_ppt(presentationPath):
    open_script = f"""
    tell application "Microsoft PowerPoint"
        activate
        open "{presentationPath}"
        set slideShowSettings to slide show settings of active presentation
        set starting slide of slideShowSettings to 4
        set ending slide of slideShowSettings to 4
        run slide show slideShowSettings
    end tell
    """
    subprocess.run(["osascript", "-e", open_script])


def open_file_dialog():
    # open a dialog for selecting a file
    file_path = filedialog.askopenfilename(
        # title of the dialog window
        title="Select a File",
        # types of files to filter in the dialog
        filetypes=[
            ("PowerPoint files", "*.pptx"),
        ],
    )
    # if a file path is selected
    if file_path:
        # display the path of the selected file
        open_ppt(file_path)


def image_processing(image_path):
    image = Image.open(image_path)
    resize_image = image.resize((150, 150))
    img = ImageTk.PhotoImage(resize_image)
    return img


# Function to update the image when the selection changes
def update_image(*args):
    selected_gesture = default_Gesture_value.get()
    image_label.config(image=gesture_images[selected_gesture])


# Initialize the main application window
root = tk.Tk()
root.title("MPPTC")

# Set the window size and make it non-resizable
root.geometry("700x400")
root.resizable(False, False)

# Define colors
# white
background_color = "#ffffff"
# celeste
left_panel_color = "#4285F4"
button_color = "#4285F4"
button_text_color = "#000308"

# Create a frame for the left panel
# Frame is like a container
left_frame = tk.Frame(root, bg=left_panel_color, width=300, height=400)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH)

# Add text to the left panel
welcome_label = tk.Label(
    left_frame,
    text="Welcome to Multimodal PPT controller ",
    font=("Helvetica", 20, "bold"),
    bg=left_panel_color,
    fg="white",
)
welcome_label.pack(padx=20, pady=20, anchor="w")

description_label = tk.Label(
    left_frame,
    text=(
        "- This is an application that allows you to control your PowerPoint presentation using gestures or voice.\n\n"
        "- Press the start button, the application will start to recognize your gesture and voice. \n"
        "- You can choose the gesture to control the application and make sure that when you perform the gesture, you can be captured by your computer's camera. "
    ),
    font=("Helvetica", 16),
    bg=left_panel_color,
    fg="white",
    justify=tk.LEFT,
    wraplength=260,
)
description_label.pack(padx=20, pady=10, anchor="w")

# Create a frame for the right panel
right_frame = tk.Frame(root, width=300, height=400)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a label to the right panel34
details_label = tk.Label(
    right_frame,
    text="Choose the Gesture",
    font=("Helvetica", 15, "bold"),
    fg="white",
)
details_label.pack(padx=20, pady=20, anchor="nw")

# Create a frame to hold the label and button
gesture_select_frame = tk.Frame(right_frame)
gesture_select_frame.pack(pady=5, padx=40, anchor="w")

# Add input fields to the right panel
entry_style = ttk.Style()
entry_style.configure("Custom.TEntry", fieldbackground="white", borderwidth=0)

image_1 = image_processing("/Users/weidongcai/Downloads/0_0.png")
image_2 = image_processing("/Users/weidongcai/Downloads/WechatIMG208501.png")

gesture_images = {
    "👉": image_1,
    "👈": image_2,
    "🫲": image_1,
    "🫱": image_2,
}
Options = [
    "👉",
    "👈",
    "🫲",
    "🫱",
]


default_Gesture_value = tk.StringVar()
# default value for select gesture menu
default_Gesture_value.set(Options[0])
default_Gesture_value.trace_add("write", update_image)
select_gesture_menu = tk.OptionMenu(
    gesture_select_frame, default_Gesture_value, *Options
)
select_file_label = tk.Label(
    # parent widget
    gesture_select_frame,
    text="Select the next Gesture",
    font=(
        "Helvetica",
        15,
    ),
    fg="white",
)
select_file_label.pack(side=tk.LEFT)
select_gesture_menu.pack(side=tk.LEFT)

image_label = tk.Label(right_frame, image=image_1)
image_label.pack()


# Create a frame to hold the label and button
file_select_frame = tk.Frame(right_frame)
file_select_frame.pack(pady=5, padx=40, anchor="w")


select_file_label = tk.Label(
    # parent widget
    file_select_frame,
    text="Select the PowerPoint",
    font=(
        "Helvetica",
        15,
    ),
    fg="white",
)

select_file_label.pack(side=tk.LEFT)
# Add a button with an icon to the right panel (icon represented as text here)
select_file_button = tk.Button(
    file_select_frame,
    text="📂",
    width=2,
    bg="white",
    command=open_file_dialog,
)
select_file_button.pack(side=tk.LEFT, padx=5)
# select_file_label.grid(row=0,column=0)


# Add a button to the right panel for start detection
start_detection_button = tk.Button(
    right_frame,
    text="Start Detection",
    bg="white",
    fg="black",
    font=("Helvetica", 12, "bold"),
    relief=tk.FLAT,
)
start_detection_button.pack(pady=20)

# image = Image.open("/Users/weidongcai/Downloads/WechatIMG208501.png")
# resize_image = image.resize((100, 100))
# img = ImageTk.PhotoImage(resize_image)
# image_label = tk.Label(right_frame, image=img)
# image_label.pack()

# Run the application
root.mainloop()
