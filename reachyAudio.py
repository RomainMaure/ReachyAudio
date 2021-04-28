from reachyAudioPlayerRecorder import ReachyAudioPlayerRecorder
from reachyAudioTextToSpeech import ReachyAudioTextToSpeech
from reachyAudioSpeechRecognition import ReachyAudioSpeechRecognition
from reachyAudioMicArrayFeatures import ReachyAudioMicArrayFeatures


class ReachyAudio(ReachyAudioPlayerRecorder, ReachyAudioTextToSpeech, ReachyAudioSpeechRecognition, ReachyAudioMicArrayFeatures):
    """ The reachyAudio module defines the ReachyAudio class.
        This class regroup all the features related to audio and natural language processing.
    """

    def __init__(self):
        ReachyAudioPlayerRecorder.__init__(self)
        ReachyAudioTextToSpeech.__init__(self)
        ReachyAudioSpeechRecognition.__init__(self)
        ReachyAudioMicArrayFeatures.__init__(self)
        
    
    def __del__(self):
        self.engine.stop()
    