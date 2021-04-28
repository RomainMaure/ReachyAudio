import pyttsx3


class ReachyAudioTextToSpeech():
    """ The ReachyTextToSpeech class allows Reachy to speak. It sends commands to 
        a text-to-speech engine, and authorizes also voice customization.
    """
    
    def __init__(self):
        print("Text to speech engine initialization...")
        self.engine = self.initializeEngine()
        self.setEngineProperties()
        print("Done")

    def initializeEngine(self):
        """ Initialize the text to speech engine. 
        
            :return: Instance of the pyttsx3 engine class.
        """
        
        return pyttsx3.init()

    def setEngineProperties(self, rate = 150, volume = 1.0, voice_id = "default"):
        """ Set the properties of the text to speech engine.

            :param rate: Speed rate of the voice.
            :param volume: Volume of the voice.
            :param voice_id: ID of the voice to be used.
        """
        
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        self.engine.setProperty('voice', voice_id)

    def speak(self, text):
        """ Allow Reachy to speak.

            :param text: Text to be said.
        """
        
        self.engine.say(text)
        self.engine.runAndWait()
        
    def availableVoices(self):
        """ Display all the available voices characteristics. """ 
        
        voices = self.engine.getProperty('voices')

        for voice in voices:
            print("Voice:")
            print(" - ID: %s" % voice.id)
            print(" - Name: %s" % voice.name)
            print(" - Gender: %s" % voice.gender)
