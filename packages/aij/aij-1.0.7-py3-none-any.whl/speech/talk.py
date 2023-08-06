import os
import time
from langchain.llms import OpenAI
from gtts import gTTS
from io import BytesIO
from pygame import mixer

user_profile = os.environ['USERPROFILE']
SEP = os.path.sep
JOKE_PATH = f"{user_profile}{SEP}Desktop{SEP}joke.mp3"


class AIJoke():
    """
    A class to tell a joke using OpenAI's API
    """

    def __init__(self, output_path=JOKE_PATH):
        self.llm = OpenAI(model_name="text-ada-001", n=2, best_of=2)
        self.answer = self.llm("Tell me a joke")
        self.answer = "\n".join([line for line in self.answer.split("\n") if line.strip() != ""])
        self.out = output_path

    def save_as_audio(self):
        """
        Save the joke as an audio file
        """
        tts = gTTS(self.answer, lang="en")
        # save to file
        tts.save(self.out)

    def play_audio(self):
        """
        Play the audio file
        """
        mixer.init()
        mixer.music.load(self.out)
        mixer.music.play()

        while mixer.music.get_busy():
            time.sleep(1)
