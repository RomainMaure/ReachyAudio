import time
import usb.core
import numpy as np
from tuning import Tuning
from threading import Thread
from pixel_ring import PixelRing
from math import cos, sin, radians


#     Mic array:
#
#       ####
#    #   90°  #
#  #            #
# # 180° TOP   0°#
# #      VIEW    #
#  #            #
#    #  270°  #
#       ####
#


detectedAngle = -1.0

def orientationCallback(mic):
    """ Callback function performing the recording of the 
        voice activity and the direction of arrival angle.
        Detects the end of a speech and average the measures
        taken to update the direction of arrival angle.

        :param mic: Instance of the Tuning class.
    """
        
    counter = 0
    voiceCounter = 1
    angles = np.array([])
    voices = np.array([])
    global detectedAngle
        
    while True:
        detectedAngle = -1
            
        # Record data
        voiceActivity = mic.is_voice()
        voices = np.append(voices, voiceActivity)
        angles = np.append(angles, mic.direction)
            
        if voiceActivity:
            counter = 0
        else:
            counter += 1
                
        voiceSamples = np.count_nonzero(voices)
                
        # If voice activity has been previously detected and there is no
        # voice activity anymore since 1 second then compute the
        # average angle
        if counter == 20 and voiceSamples > 2:
            counter = 0
            doNotConsider = voiceSamples // 2
            voiceCounter = 1
            detectedAngle = 0
            numberDetections = 0
            for voice, angle in zip(voices, angles):
                if voice:
                    # Do not take into acount the first samples of
                    # voice activity as the first measures of
                    # angle are othen strongly correlated to the last
                    # angle detected
                    if voiceCounter > doNotConsider:
                        detectedAngle += angle
                        numberDetections += 1
                    else:
                        voiceCounter += 1
                           
            detectedAngle /= numberDetections
            voices = np.array([])
            angles = np.array([])
                
        # if nobody speak during a long time, reset the array
        # to avoid too high array lenght
        elif counter > 20 and voiceSamples <= 5:
            counter = 0
            voices = np.array([])
            angles = np.array([])
            
        if detectedAngle != -1:
            time.sleep(0.5)
        else:
            time.sleep(0.05)


class ReachyAudioMicArrayFeatures():
    """ This class regroup all the features related to the built-in
        algorithms provided by the manufacturers of Reachy's microphone array.
        It mainly allows to do voice activity detection, detects the
        direction of arrival of sounds and use this data to make
        Reachy's head orients toward the interlocutor.
    """
    
    def __init__(self):
        # Initialize the mic object
        print("Mic object initialization...")
        self.mic = None
        self.pixel_ring = None
        dev = usb.core.find(idVendor= 0x2886, idProduct= 0x0018)
        if dev:
            self.mic = Tuning(dev)
            self.pixel_ring = PixelRing(dev)
            print("Done")
        else:
            print("Error when trying to access the mic object.")
            print("The methods requiring the microphone won't be able to execute.")
            print("For more documentation, see the section ReachyAudioMicArrayFeatures in the README file.")
            
        # Initialize the thread for data recording of voice activity 
        # and voice orientation
        if self.mic is not None:
            print("Recording thread initialization...")
            recordingThread = Thread(target= orientationCallback, args=(self.mic,))
            recordingThread.start()
            print("Done")
            
    ########################################################################
    ############################ VOICE ACTIVITY ############################
    ########################################################################
    
    def longIsVoice(self, numberMeasures = 40, timeDelay = 0.1):
        """ Allows to make several measurements of voice activity spaced in time.

            :param numberMeasures: Number of measurements to be done.
            :param timeDelay: Time delay between each measurement.
            :return: List of voice activity measures.
        """
        
        recording = []
        
        if timeDelay < 0.01:
            timeDelay = 0.01
            
        if self.mic is not None:
            print("Start")
            for _ in range(numberMeasures):
                sample = self.mic.is_voice()
                recording.append(sample)
                print(sample)
                time.sleep(timeDelay)
            print("End")
        else:
            print("mic is None")
            
        return recording
    
    ########################################################################
    ########################## SOUND LOCALIZATION ##########################
    ########################################################################

    def longSoundOrientation(self, numberMeasures = 40, timeDelay = 0.1):
        """ Allows to make several measurements of sound orientation spaced in time.

            :param numberMeasures: Number of measurements to be done.
            :param timeDelay: Time delay between each measurement.
            :return: List of incomming sound orientation measures.
        """
        
        recording = []
        
        if timeDelay < 0.01:
            timeDelay = 0.01
            
        if self.mic is not None:
            print("Start")
            for _ in range(numberMeasures):
                sample = self.mic.direction
                recording.append(sample)
                print(sample)
                time.sleep(timeDelay)
            print("End")
        else:
            print("mic is None")
            
        return recording
    
    def getDetectedAngle(self):
        """ Return the direction of arrival angle computed 
            in the orientation callback.
            
            :return: Direction of arrival angle computed after 
            the end of a speech has been detected.
        """
        
        global detectedAngle
        
        return detectedAngle

    def orientToInterlocutor(self, reachyObject):
        """ Allows Reachy's head to orient toward the interlocutor
            by using the direction of arrival angle.

            :param reachyObject: Instance of the Reachy class.
            Allows to run the motors commands to move Reachy's head.
        """
        
        if self.mic is not None:
            print("Listening...")
            while True:
                angle = self.getDetectedAngle()
                if angle != -1.0:
                    print("Heared a voice at ", angle, "degrees.")
                    theta = radians(angle)
                    reachyObject.head.compliant = False
                    reachyObject.head.look_at(2, cos(theta), sin(theta)-0.3, duration=2, wait=True)
                    time.sleep(0.1)
                    break
        else:
            print("mic is None")
