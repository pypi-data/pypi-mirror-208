# Speech Recognition Wrapper

[![PyPI package](https://img.shields.io/badge/pip%20install-grokspeechrec-blue)](https://pypi.org/project/grokspeechrec/)  &nbsp;  [![version number](https://img.shields.io/pypi/v/grokspeechrec?color=red&label=version)](https://pypi.org/project/grokspeechrec/releases)  


---

This package is a wrapper for [Speech Recognition Module](https://github.com/Uberi/speech_recognition#readme), created to import directly and transcribe Speech Input. You would need a Microphone input and a Speaker output connected to your environment before starting.

## Installation
This package comes with internal dependency of PyAudio and Vosk model.
The package installation takes care of installing all the dependecies, by performing the following steps:

```bash
pip install --upgrade grokspeechrec
```

## Usage
Once you have it installed, import the module and use it to pass Microphone Speech as shown below:

```python
from grokspeechrec import speechrec

rec = speechrec.app.Recognize()
output = rec.recognize(rec.recognizer)
```

The `output` will contain the transcribed results.


