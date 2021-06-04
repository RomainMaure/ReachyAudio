"""This module defines the ReachyAudioPlayerRecorder class."""

import wave
import pyaudio


class ReachyAudioPlayerRecorder():
    """ReachyAudioPlayerRecorder class.

    This class allows to record audio samples and save them as WAV file.
    It also allows to play WAV files.
    """

    def __init__(self):
        """Define constants for playing and recording."""
        # number of frames the signal is split into
        self.chunk = 1024

        # number of frames per second
        self.rate = 44100

        # number of samples per frame
        self.channels = 2

        # number of bytes per sample
        self.format = pyaudio.paInt16

    def recordAudio(self, recordTime=5, wavOutputFileName="output.wav"):
        """Record audio samples and save them as a WAV file.

        :param recordTime: Duration of the recording.
        :param wavOutputFileName: Name of the WAV output file.
        """
        try:
            # Create the PyAudio object and open the PyAudio stream
            p = pyaudio.PyAudio()
            stream = p.open(format=self.format,
                            channels=self.channels,
                            rate=self.rate,
                            input=True,
                            frames_per_buffer=self.chunk)

            print("* recording")

            frames = []

            # our signal is composed of rate*recordTime frames. Since our for
            # loop is not repeated for each frame but only for each chunk,
            # the number of loops has to be divided by the chunk size
            for _ in range(int(self.rate / self.chunk * recordTime)):
                data = stream.read(self.chunk)
                frames.append(data)

            print("* done recording")

            # Close and terminate the PyAudio processes
            stream.stop_stream()
            stream.close()
            p.terminate()

            # Save the recorded audio data
            wf = wave.open(wavOutputFileName, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()

        except Exception as e:
            print("Exception: " + str(e))

    def playAudio(self, wavFileName):
        """Play a WAV file.

        :param wavFileName: Name of the WAV file to play.
        """
        try:
            # Open the wav file
            wf = wave.open(wavFileName, 'rb')

            # Create the PyAudio object and open the PyAudio stream
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            # Read the wav file until his end
            data = wf.readframes(self.chunk)

            while data != b'':
                stream.write(data)
                data = wf.readframes(self.chunk)

            # Terminate and close all the processes
            stream.stop_stream()
            stream.close()

            p.terminate()

            wf.close()

        except Exception as e:
            print("Exception: " + str(e))
