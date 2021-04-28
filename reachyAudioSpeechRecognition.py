import speech_recognition as sr


class ReachyAudioSpeechRecognition():
    """ The ReachySpeechRecognition class allows Reachy to recognize speech. """
    
    def __init__(self):
        print("Recognizer initialization...")
        self.microphone = self.initializeMicrophone()
        self.recognizer = self.initializeRecognizer()
        self.calibrateRecognizer()
        print("Done")

    def initializeRecognizer(self):
        """ Initialize the recognizer object. 
        
            :return: Instance of the Recognizer class.
        """
        
        return sr.Recognizer()

    def initializeMicrophone(self):
        """ Initialize the microphone object. 
        
            :return: Instance of the Microphone class.
        """
        
        return sr.Microphone()

    def calibrateRecognizer(self):
        """ Calibrate the recognizer to ambient noise. """
        
        with self.microphone as source:
            # listen for 1 second to calibrate the energy threshold for ambient noise levels
            print("Calibrating: please do not speak")
            self.recognizer.adjust_for_ambient_noise(source)
            print("Calibrating done")
            
    def recognizeSpeech(self):
        """ Recognize the incomming speech. 
        
            :return: The recognized text if the recognition worked
            or an empty string otherwise.
        """

        with self.microphone as source:
            print("Say something")
            
            audio = self.recognizer.listen(source)
            said = ""
            
            try:
                said = self.recognizer.recognize_google(audio)
                print(said)
            except Exception as e:
                print("Exception: " + str(e))
                
            return said.lower()
            