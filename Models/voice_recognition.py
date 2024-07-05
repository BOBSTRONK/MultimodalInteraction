import speech_recognition as sr
import re
import os


class VoiceRecognizer:
    recognizer = sr.Recognizer()

    # Define a list of keywords/phrases that indicate switching slides
    keywords_next = [
        "switch to the next slide",
        "go to the next slide",
        "next slide",
        "change to the next slide",
        "move to the next slide",
        "switch to the next page",
        "go to the next page",
        "next page",
        "change to the next page",
        "move to the next page",
        "next slide please",
        "next page please",
        "go on to the next slide",
        "go on to the next page",
        "go on",
        "go next",
    ]
    keywords_previous = [
        "switch to the previous slide",
        "go to the previous slide",
        "previous slide",
        "change to the previous slide",
        "move to the previous slide",
        "switch to the previous page",
        "go to the previous page",
        "previous page",
        "change to the previous page",
        "move to the previous page",
        "previous slide please",
        "previous page please",
        "go back to the previous slide",
        "go back to the previous page",
        "go back",
        "go previous",
    ]

    def __init__(self):
        self.value = None

    def check_for_keywords(self, sentence):
        for keyword in self.keywords_next:
            if sentence.strip() == keyword:
                return "next"

        for keyword in self.keywords_previous:
            if sentence.strip() == keyword:
                return "previous"
        return None

    def microphone(self):
        while True:
            try:
                with sr.Microphone() as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, duration=0.1)
                    print("Listening...")
                    audio = self.recognizer.listen(mic)
                    text = self.recognizer.recognize_google(audio)
                    text = text.lower()
                    print(f"You said: {text}")

                    # Split the recognized text into sentences using a regular expression
                    sentences = re.split(r"[.!?]", text)
                    sentences = [
                        sentence.strip() for sentence in sentences if sentence.strip()
                    ]

                    if self.check_for_keywords(text) == "next":
                        self.value = "next"
                        os.system(
                            'osascript -e \'display notification "Switch to Next slide" with title "Voice recognition"\''
                        )
                        print("next")
                    elif self.check_for_keywords(text) == "previous":
                        self.value = "previous"
                        os.system(
                            'osascript -e \'display notification "Switch to Previous slide" with title "Voice recognition"\''
                        )
                        print("previous")
            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
                # os.system('osascript -e \'display notification "Sorry, I did not understand that." with title "Error message"\'')


# if __name__ == '__main__':
#    voice_recognizer = VoiceRecognizer()
#    voice_recognizer.microphone()
