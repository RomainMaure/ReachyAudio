"""This module defines the ReachyAudioTextToSpeech class."""

import time
import pyttsx3
import numpy as np
import scipy.io.wavfile as sc
from gtts import gTTS
from pydub import AudioSegment
from .reachyAudioPlayerRecorder import ReachyAudioPlayerRecorder


class ReachyAudioTextToSpeech():
    """The ReachyTextToSpeech class allows Reachy to speak.

    It sends commands to a text-to-speech engine, and authorizes also voice
    customization.
    """

    def __init__(self):
        """Initialize the text to speech engine."""
        print("Text to speech engine initialization...")
        self.engine = self.initializeEngine()
        self.setEngineProperties()
        self.reachyAudioPlayerRecorderObject = ReachyAudioPlayerRecorder()
        print("Done")

    def initializeEngine(self):
        """Initialize the text to speech engine.

        :return: Instance of the pyttsx3 engine class.
        """
        return pyttsx3.init()

    def setEngineProperties(self, rate=150, volume=1.0, voice_id="default"):
        """Set the properties of the text to speech engine.

        :param rate: Speed rate of the voice.
        :param volume: Volume of the voice.
        :param voice_id: ID of the voice to be used.
        """
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        self.engine.setProperty('voice', voice_id)

    def speak(self, text, alteredVoice=False):
        """Allow Reachy to speak.

        :param text: Text to be said.
        :param alteredVoice: If we want Reachy's voice to sound more
                             robotic like.
        """
        if not alteredVoice:
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            # Create an audio file containing the speech to alter
            tts = gTTS(text)
            tts.save('voiceToAlter.mp3')
            sound = AudioSegment.from_mp3('voiceToAlter.mp3')
            sound.export('voiceToAlter.wav', format='wav')

            # Alter the previously created audio file
            outputFileName = self.diodeRingModulator('voiceToAlter.wav')

            # Play the altered audio file
            self.reachyAudioPlayerRecorderObject.playAudio(outputFileName)
            time.sleep(0.5)

    def availableVoices(self):
        """Display all the available voices characteristics."""
        voices = self.engine.getProperty('voices')

        for voice in voices:
            print("Voice:")
            print(" - ID: %s" % voice.id)
            print(" - Name: %s" % voice.name)
            print(" - Gender: %s" % voice.gender)

    def diode(self, signalArray):
        """Apply an approximation of the diode non linearity model.

        The approximation of the diode is described by:

               { 0           , if x <= 0
        f(x) = |
               { 0.1*x^(1.7) , if x > 0


        :param signalArray: The signal to be altered.
        :return: The signal altered by the diode non linearity.
        """
        diodeArray = [0.1*(x**1.7) if x > 0 else 0.0 for x in signalArray]

        return np.array(diodeArray)

    def diodeRingModulator(self, intputFileName):
        """Simulate a diode ring modulator electrical circuit.

        Alter the audio file containing the text to be said to make it sounds
        more robotic like.

        :param intputFileName: Name of the audio file containing the voice to
                               be altered.
        :return: Name of the altered audio file.
        """
        # Read the audio file
        [_, data] = sc.read(intputFileName)

        # Get maximum absolute value of input signal
        maxVal = max(abs(data))

        # Scale down the input signal
        scaledData = data/maxVal

        # Create carrier signal
        fCarrier = 500
        t = np.linspace(0, len(scaledData), len(scaledData))
        carrier = np.sin(2*np.pi*fCarrier*t)

        # Compute output of the ring modulator circuit
        topFirst = carrier + 0.5*scaledData
        top = self.diode(topFirst) + self.diode(-topFirst)

        bottomFirst = carrier - 0.5*scaledData
        bottom = self.diode(bottomFirst) + self.diode(-bottomFirst)

        output = top - bottom

        # Scale back
        output = 5*maxVal*output

        # Save the signal
        sc.write('alteredVoice.wav', 22050, np.int16(output))

        return 'alteredVoice.wav'
