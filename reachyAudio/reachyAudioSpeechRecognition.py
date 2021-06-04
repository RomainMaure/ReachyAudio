"""This module defines the ReachyAudioSpeechRecognition class."""

import speech_recognition as sr

detectedSentence = ""
robotSpeaking = False


def speechRecognitionCallback(recognizer, audio):
    """Recognize the received audio data and update detectedSentence.

    The callback called when we receive audio data (when the interlocutor
    stopped to speak).
    """
    global robotSpeaking
    global detectedSentence

    if not robotSpeaking:
        try:
            detectedSentence = recognizer.recognize_google(audio)
        except:
            detectedSentence = ""


class ReachyAudioSpeechRecognition():
    """The ReachySpeechRecognition class allows Reachy to recognize speech."""

    def __init__(self):
        """Initialize the microphone and the recognizer objects."""
        print("Recognizer initialization...")
        self.microphone = self.initializeMicrophone()
        self.recognizer = self.initializeRecognizer()
        self.calibrateRecognizer()
        print("Done")

    def initializeRecognizer(self):
        """Initialize the recognizer object.

        :return: Instance of the Recognizer class.
        """
        return sr.Recognizer()

    def initializeMicrophone(self):
        """Initialize the microphone object.

        :return: Instance of the Microphone class.
        """
        return sr.Microphone()

    def calibrateRecognizer(self):
        """Calibrate the recognizer to ambient noise."""
        with self.microphone as source:
            # listen for 5 second to calibrate the energy threshold for ambient
            # noise levels
            print("Calibrating: please do not speak")
            self.recognizer.adjust_for_ambient_noise(source, 5)
            print("Calibrating done")

    def recognizeSpeech(self):
        """Recognize the incomming speech.

        :return: The recognized text if the recognition worked or an empty
                 string otherwise.
        """
        with self.microphone as source:
            print("Say something")

            audio = self.recognizer.listen(source)
            said = ""

            try:
                said = self.recognizer.recognize_google(audio)
                print(said)
            except:
                print("Sorry, I haven't understand you properly, \
                       would you mind to speak louder/slower/closer ?")

            return said.lower()

    def getDetectedSentence(self):
        """Get the last detected sentence.

        :return: The last detected sentence.
        """
        global detectedSentence
        return detectedSentence

    def clearDetectedSentence(self):
        """Clear the last detected sentence."""
        global detectedSentence
        detectedSentence = ""

    def setRobotSpeaking(self):
        """Set that the robot is currently speaking.

        Allow to not run the code in the recognition thread.
        """
        global robotSpeaking
        robotSpeaking = True

    def clearRobotSpeaking(self):
        """Set that the robot is not speaking anymore.

        Allow to run the code in the recognition thread.
        """
        global robotSpeaking
        robotSpeaking = False
