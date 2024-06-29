import speech_recognition as sr
import pyttsx3
import re

recognizer = sr.Recognizer()

# Define a list of keywords/phrases that indicate switching slides
keywords = [
    "switch to the next slide", "go to the next slide", "next slide", "change to the next slide", "move to the next slide",
    "switch to the next page", "go to the next page", "next page", "change to the next page", "move to the next page",
    "switch to the previous slide", "go to the previous slide", "previous slide", "change to the previous slide", "move to the previous slide",
    "switch to the previous page", "go to the previous page", "previous page", "change to the previous page", "move to the previous page",
    "next slide please", "next page please", "previous slide please", "previous page please",
    "go back to the previous slide", "go back to the previous page"
]

def check_for_keywords(sentence, keywords):
    for keyword in keywords:
        if sentence.strip() == keyword:
            return True
    return False

while True:
    try:
        with sr.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic, duration=0.2)
            print("Listening...")
            audio = recognizer.listen(mic)
            text = recognizer.recognize_google(audio)
            text = text.lower()
            print(f"You said: {text}")

            # Split the recognized text into sentences using a regular expression
            sentences = re.split(r'[.!?]', text)
            sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

            if check_for_keywords(text, keywords):
                print("Good job")
        
    except sr.UnknownValueError:
        recognizer = sr.Recognizer()
        continue