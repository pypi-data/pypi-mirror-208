# crack https://github.com/Eddie2111/ProblemSolvers/commit/a109ac434465359db62f41d9c7dddc8c2f37924e
# model = Model("Vosk/vosk-model-en-in-0.5") 


from vosk import Model, KaldiRecognizer
import pyaudio
import os
import sys
import platform
import subprocess
from glob import glob
import urllib.request
import zipfile

MODEL_PTH = os.path.join(os.path.dirname(__file__), "Vosk")
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-en-us-daanzu-20200905-lgraph.zip"
OSYS = platform.system()

if not os.path.exists(MODEL_PTH):
    os.mkdir(MODEL_PTH)
    print("Created Model Folder")

class Recognize(object):

    def __init__(self):
        ZIP_PTH = os.path.join(MODEL_PTH, "vosk-model-en-us-daanzu-20200905-lgraph.zip")
        resp = urllib.request.urlretrieve(MODEL_URL, ZIP_PTH)
        with zipfile.ZipFile(ZIP_PTH, 'r') as zip_ref:
            zip_ref.extractall(MODEL_PTH)

        self.model = Model(os.path.join(MODEL_PTH, "vosk-model-en-us-daanzu-20200905-lgraph"))
        self.recognizer = KaldiRecognizer(self.model,16000)

    def __str__(self):
        return """Class to initiate speech recognizer"""

    def recognizer(self):
        return self.recognizer

    @classmethod
    def recognize(self, recognizer_model):
        mic = pyaudio.PyAudio()
        stream = mic.open(rate=16000, channels=1, format=pyaudio.paInt16,input=True, frames_per_buffer=8192)
        stream.start_stream()
        print('start speaking')

        while True:
            data = stream.read(4096)
            if len(data) == 0:
                break
            if recognizer_model.AcceptWaveform(data):
                x = recognizer_model.Result()
                print(x)
                break
        return x
