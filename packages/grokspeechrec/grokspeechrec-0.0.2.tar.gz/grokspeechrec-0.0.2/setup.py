from setuptools import setup, find_packages
import os
import sys
import platform
import subprocess
from setuptools.command.install import install
from glob import glob

class CustomInstallCommand(install):
    def run(self):
        print("Running custom install command for PyAudio")
        # Your custom install code goes here
        install.run(self)
        
        operatingsystem = platform.system()

        if operatingsystem == "Linux":
            try:
                subprocess.call(["sudo apt-get update"], shell=True)
                subprocess.call(["sudo apt-get upgrade"], shell=True)
                subprocess.call(["sudo apt-get install portaudio19-dev"], shell=True)
                subprocess.call(["sudo pip install pyaudio"], shell=True)
            except:
                print(f"Installation failed on system {operatingsystem}")
                print(f"Kindly install PyAudio using Installation Journal")
        else:
            try:
                os.execv(sys.executable, ["python", "-m", "pip", "install", "pyaudio"])
            except:
                print(f"Installation failed on system {operatingsystem}")
                print(f"Kindly install PyAudio using pip install pyaudio")


with open("README.md", "rb") as fh:
    long_description = fh.read().decode("utf-8")

setup(
    name='grokspeechrec',
    version='0.0.2',
    license='MIT',
    author="GROKLEARNING",
    author_email='visalakshi2001@gmail.com',
    description = "TEST APP TMLC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages= ["grokspeechrec", "grokspeechrec.speechrec"],
    package_dir={'grokspeechrec': 'src'},
    py_modules=["grokspeechrec.speechrec.app"],
    url='https://github.com/visalakshi2001/grokspeechrec/',
    keywords='speech recognizer',
    setup_requires=['vosk'],
    install_requires=['vosk'],
    cmdclass={
        'install': CustomInstallCommand,
    },
    # data_files= glob("./src/speechrec/Vosk/**/*", recursive=True),
    # package_data= {'': glob("./src/speechrec/Vosk/**/**", recursive=True)},
)