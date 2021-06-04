"""The reachyAudio module defines the ReachyAudio class."""

import time
from math import cos, sin, radians

from .reachyAudioPlayerRecorder import ReachyAudioPlayerRecorder
from .reachyAudioTextToSpeech import ReachyAudioTextToSpeech
from .reachyAudioMicArrayFeatures import ReachyAudioMicArrayFeatures
from .reachyAudioAnswering import ReachyAudioAnswering
from .reachyAudioSpeechRecognition import ReachyAudioSpeechRecognition
from .reachyAudioSpeechRecognition import speechRecognitionCallback


class ReachyAudio(ReachyAudioPlayerRecorder,
                  ReachyAudioTextToSpeech,
                  ReachyAudioSpeechRecognition,
                  ReachyAudioMicArrayFeatures,
                  ReachyAudioAnswering):
    """ReachyAudio class.

    This class regroup all the features related to audio and natural
    language processing.
    """

    def __init__(self):
        """Call the constructor of each submodule."""
        ReachyAudioPlayerRecorder.__init__(self)
        ReachyAudioTextToSpeech.__init__(self)
        ReachyAudioSpeechRecognition.__init__(self)
        ReachyAudioMicArrayFeatures.__init__(self)
        ReachyAudioAnswering.__init__(self)

    def __del__(self):
        """Delete the text to speech engine."""
        self.engine.stop()

    def conversation(self, reachyObject, alteredVoice=False):
        """Allow Reachy to converse with people.

        :param reachyObject: Instance of the Reachy class.
        :param alteredVoice: If we want Reachy's voice to sound more
                             robotic like.
        """
        # Allow to store the detected angle as the recognition thread
        # takes more time to detect the end of a voice sample than the
        # recording thread
        stored_angle = -1

        # Use the LEDs to make the conversation more interactive
        self.pixel_ring.set_brightness(0x12)
        self.pixel_ring.set_color_palette(self.COLORS['ORANGE'],
                                          self.COLORS['YELLOW'])
        self.pixel_ring.speak()

        # Initialize the recognition thread so that we can do both recognition
        # and orientation detection
        stop_listening = self.recognizer.listen_in_background(
                                                    self.microphone,
                                                    speechRecognitionCallback)
        print("Listening...")

        while True:
            try:
                # Try to detect if someone spoke
                said = self.getDetectedSentence()
                angle = self.getDetectedAngle()
                if angle != -1:
                    stored_angle = angle
                if said != "":

                    # Reachy heard and recognized a sentence, he will now
                    # answer to it. We set that the robot is speaking such that
                    # we don't try to recognize what he will say. We also
                    # change the LEDs color to show to the interlocutor than
                    # Reachy is now in the answering state
                    self.setRobotSpeaking()
                    self.setRobotSpeakingMic()
                    self.pixel_ring.set_color_palette(self.COLORS['MAGENTA'],
                                                      self.COLORS['CYAN'])
                    print("Reachy heared a voice at ", stored_angle,
                          "degrees.")
                    print("Reachy thinks you said: ", said)

                    # Move the head toward the interlocutor
                    theta = radians(stored_angle)
                    reachyObject.head.compliant = False
                    reachyObject.head.look_at(2, cos(theta), sin(theta)-0.3,
                                              duration=2, wait=True)

                    # Answer to the interlocutor
                    tag, answer = self.answer(said)
                    self.speak(answer, alteredVoice=alteredVoice)
                    time.sleep(2)

                    # End of the conversation depending on the sentence intent
                    if tag == "goodbye":
                        break

                    # Reachy stoped to speak, we reactivate the recording
                    # thread and the recognition thread. We also change the
                    # LEDs color to show to the interlocutor than Reachy is
                    # now in the listening state
                    self.clearDetectedSentence()
                    self.clearDetectedAngle()
                    self.clearRobotSpeakingMic()
                    self.clearRobotSpeaking()
                    self.pixel_ring.set_color_palette(self.COLORS['ORANGE'],
                                                      self.COLORS['YELLOW'])
                    print("Listening...")

                time.sleep(0.1)

            # End of the conversation if keyboard interrupt
            except KeyboardInterrupt:
                break

        # End of the conversation, we stop the recognition thread
        stop_listening(wait_for_stop=True)
        self.clearDetectedSentence()
        self.clearDetectedAngle()
        self.clearRobotSpeakingMic()
        self.clearRobotSpeaking()
        self.pixel_ring.set_color_palette(self.COLORS['ORANGE'],
                                          self.COLORS['YELLOW'])
        print("End of conversation !")
