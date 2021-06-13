# Reachy Audio

The purpose of the ReachyAudio library is to provide to Reachy basic features 
related to audio.

These features are mainly : 
- Recording audio files.
- Playing audio files.
- Making Reachy speak.
- Synthesize Reachy's voice to make it sound more robotic like.
- Recognizing what an interlocutor is saying.
- Detecting voice activity.
- Computing direction of arrival of sounds.
- Making reachy's head orients to the person which is currently speaking.
- Control the LEDs of the microphone array.
- Allowing Reachy to answer to simple questions.

The jupyter notebook named ReachyAudioNotebook shows an example on how to use this library.

## ReachyAudio

All of the features described above are grouped in a class named ReachyAudio
that inherits from other subclasses.

The goal of this class is to simplify the use of the library. The user only has 
to create an instance of the ReachyAudio class and can then call all the methods
implemented in the library.

Some methods in the library can be called with parameters. The goal of these 
parameters is to provide flexibility to the user by allowing him to adapt the 
library's methods to his specific goal.
For example, if you want the robot to say a text orally, you can specify the
rate and the volume of the voice as well as the accent that should be used.
The class also provide some default parameters in the case you don't want to 
specify them.

Finally this class also contains the method named conversation. This method 
uses each part of the library in order to allow Reachy to do a simple conversation 
with people.


https://user-images.githubusercontent.com/63020507/121800805-2ec59b00-cc34-11eb-9ccd-d2e23f30eb4f.mp4



## ReachyAudioPlayerRecorder

This class allows to record audio samples and save them as WAV file. It also allows to play WAV files.

To record audio samples, one can call the method named recordAudio. By default, the record time is five seconds and the name of the output file is "output.wav". However, it is possible to specify them.

To play audio, one can call the method named playAudio.

The audio recorder and the audio player are implemented using basic features provided by the [PyAudio](https://pypi.org/project/PyAudio/) library.
The [Wave](https://pypi.org/project/Wave/) library allows to properly save what has been recorded in an output WAV file or open and load the data to be played from a WAV file.


https://user-images.githubusercontent.com/63020507/121801316-0c814c80-cc37-11eb-8f3a-8c57cedd3c21.mp4



## ReachyAudioTextToSpeech

The ReachyAudioTextToSpeech class allows Reachy to speak.

By using the method speak, you can make Reachy says any text you want.

The method setEngineProperties allows to specify some parameters of the text to speech engine such as the rate of the voice (default is 150), the volume of the voice (default is 1.0) and even the desired voice itself (the default one is english).

The method availableVoices can be used to print all the voices that are on your system and that can be used.

To implement these methods, the [pyttsx3](https://pypi.org/project/pyttsx3/) library is used.

The method speak also provides a synthesizer feature whose goal is to alter default text to speech voice into a voice that sounds more robotic for Reachy.
Due to some bugs with the method save_to_file of the pyttsx3 library, this synthesizer feature uses the [gTTS](https://pypi.org/project/gTTS/) library instead.
The synthesized voice will thus be always the same and the method setEngineProperties won't have any effects on it.
Finally, this synthesizer also uses the [numpy](https://pypi.org/project/numpy/), [scipy](https://pypi.org/project/scipy/) and [pydub](https://pypi.org/project/pydub/) libraries.


https://user-images.githubusercontent.com/63020507/121801323-12772d80-cc37-11eb-88f0-f07c47f42898.mp4


https://user-images.githubusercontent.com/63020507/121801326-173be180-cc37-11eb-8165-d9f3dc3c8c39.mp4



## ReachyAudioSpeechRecognition

The ReachyAudioSpeechRecognition class allows Reachy to recognize speech.

The class constructor initializes a recognizer object and calibrates it. The calibration step lasts one second and allows to calibrate the energy threshold for ambiant noise levels. 

The method named recognizeSpeech waits until the user says something and stops the listening when the user stops to speak. At the end, it returns the text that has been orally said. 

It is important to notice that the recognizer does not always succed to recognize correctly the text that has been orally said. The success rate of the recognizer depends on the distance of the person speaking to the microphone but also on the way of speaking (volume, rate, voice articulation...).

This module also provides a callback that allows to do the recognizing step by using threads (see explanations in the section bellow).

To implement this module, the [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) library is used. This library regroups several recognizer provided by different companies such as Google, IBM, Microsoft etc. For this module, i used the default recognizer of the SpeechRecognition library which is the google one. This recognizer does not require to create specific account to use it.


https://user-images.githubusercontent.com/63020507/121801330-1dca5900-cc37-11eb-9c92-74a24bc14f61.mp4



## ReachyAudioMicArrayFeatures

The ReachyAudioMicArrayFeatures class allows to acces the built-in algorithms provided by the manufacturers of the microphone array. Based on these built-in algorithms, it also provides more high level interactions for Reachy.

Among the features provided by the manufacturers of the microphone array, the ones that are mainly used in this class are the voice activity detection feature and the direction of arrival angle feature.
These two measures can be accessed by using respectively the methods named isVoice and soundOrientation.
The methods longIsVoice and longSoundOrientation allow to make respectively several measurements of voice activity and sound orientation spaced in time.

The method orientToInterlocutor allows Reachy's head to orient toward the interlocutor. It works by using a thread that will record in background the voice activity and the direction of arrival angle. This thread detects when the interlocutor stops to speak and then use the previously recorded measures to orient Reachy's head.

One of the goal of this library is to implement a complete human computer interaction with audio allowing Reachy to understand what his interlocutor is saying, orient to the interlocutor and give him back a coherent answer. To do so, one need to both record what the interlocutor is saying to recognize it afterward and record at the same time the direction of arrival of the sound to make Reachy's head orient to his interlocutor. Merging the recording of direction of arrival angle thread with the recognizing thread would thus allow to make this human computer interaction possible and realistic.

Another feature is the access to the LEDs of the microphone array of Reachy. The use of theses LEDs can significantly improve the human computer interaction by giving feedback to the interlocutor such as the internal state of the robot (listening, processing data, answering, etc...).

Note : To acces the microphone array, make sure that you have installed the [spidev](https://pypi.org/project/spidev/) library and the [pyusb](https://pypi.org/project/pyusb/) library. If the mic object fails to initialize, the problem probably comes from a denied acces due to insufficient permissions. In this case, you have to manually add the permission in a .rules file. These two links can help : [pyusb access denied](https://stackoverflow.com/questions/53125118/why-is-python-pyusb-usb-core-access-denied-due-to-permissions-and-why-wont-the) and [pyusb communication](https://stackoverflow.com/questions/31992058/how-can-i-comunicate-with-this-device-using-pyusb/31994168#31994168).
In our case, the line that we added in the .rules file was : 

```
SUBSYSTEM=="usb", ATTRS{idVendor}=="2886",ATTR{idProduct}=="0018", MODE="0666"
```

For more documentation on the microphone array of Reachy, see : [ReSpeaker_Mic_Array_v2.0](https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/)


https://user-images.githubusercontent.com/63020507/121801345-2753c100-cc37-11eb-89a5-69e4e6a9f68c.mp4


https://user-images.githubusercontent.com/63020507/121801432-831e4a00-cc37-11eb-8e0d-b39d3a7ae3c1.mp4




## ReachyAudioAnswering

The ReachyAudioAnswering class implements a small neural network allowing Reachy to answer to simple questions. To make it flexible, it uses sentence tokenizing and word stemming such that the network can provide answers to sentences different to the one used for the training. These input sentences have to remain close to the training sentences however.

Most of the methods are utility methods used for the training of the network. The method named answer is the only one used outside of the class (in the conversation method of the ReachyAudio class) and allows to provide coherent answers to the questions of the interlocutor.

The training set is located in the intents.json file. Each sentence intent is characterized by a tag which is what the network should output. The patterns list correspond to all the sentences sharing the same tag and are the network inputs. Each intent has a set of predefined responses. Once the intent of the interlocutor's sentence is determined, we just randomly output one of the responses corresponding to this specific intent.

Note : You can modify this intents.json file to adapt the network to your specific conversation.

Once the training of the network's model is done, the model and the training data are saved such that the training does not have to be executed every time a reachyAudio object is instantiated. If you change the intents.json file, you will thus have to delete the model file and the data.pickle file, otherwise the previous model will continue to be used even if you changed the intents.json file.

This class uses several python libraries. The network is done using Pytorch while the sentence processing uses nltk (Natural Language Toolkit). The class also uses the json library to properly read the intents.json file and the pickle library to store the training data as well as the vocabulary of the network. Be sure to have all these libraries installed.

Note : The installation of Pytorch on Reachy's raspberry pi requires to use wheel files and to install some dependencies. You can download the files torch-1.8.0a0+56b43f4-cp37-cp37m-linux_armv7l.whl and torchvision-0.9.0a0+8fb5838-cp37-cp37m-linux_armv7l.whl from the following [github repo](https://github.com/sungjuGit/PyTorch-and-Vision-for-Raspberry-Pi-4B).
Then you can run on the terminal the following commands :

```
sudo pip3 install torch-1.8.0a0+56b43f4-cp37-cp37m-linux_armv7l.whl
sudo pip3 install torchvision-0.9.0a0+8fb5838-cp37-cp37m-linux_armv7l.whl
sudo apt install libopenblas-dev libblas-dev m4 cmake cython python3-dev python3-yaml python3-setuptools
sudo apt-get install libavutil-dev libavcodec-dev libavformat-dev libswscale-dev
```

Note : The nltk library might require to download punkt. To do this, you can run the following commands in a terminal :

```
python3
import nltk
nltk.download('punkt')
```

## Note

Author : Romain Maure. Work carried out as part of a semester project at the CHILI (Computer Human Interaction for Learning and Instruction) laboratory, EPFL.

Supervisors : Barbara Bruno, Victor Borja Guimera, Utku Norman.

License : MIT License.
