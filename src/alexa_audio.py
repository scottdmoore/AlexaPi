
import pyaudio
import wave
import subprocess
import speech_recognition
import time
import alsaaudio
import webrtcvad
import vlc
from collections import deque


__author__ = "NJC"
__license__ = "MIT"


class AlexaAudio:
    """ This object handles all audio playback and recording required by the Alexa enabled device. Audio playback
        and recording both use the PyAudio package.

    """
    def __init__(self):
        """ AlexaAudio initialization function.
        """
        # Initialize pyaudio
        parametersCommon = [
            # '--alsa-audio-device=mono'
            # '--file-logging'
            # '--logfile=vlc-log.txt'
        ]

        parametersSpeech = parametersCommon

        parametersSpeech.append('--aout=alsa')

        parametersSpeech.append('--alsa-audio-device=plughw:1')

        self.vlc_instance = vlc.Instance(*parametersSpeech)
        self.player = self.vlc_instance.media_player_new()

        self.media_vlc_instance = self.vlc_instance
        self.media_player = self.player

        self.volume = 80

        self.queue = deque()

        return
        #self.pyaudio_instance = pyaudio.PyAudio()
        #self.im = importlib.import_module('playback_handlers.vlchandler', package=None)
        #self.cl = getattr(im, 'VlcHandler')
        #self.pHandler = cl(config, playback_callback)
        #self.player = Player(config, platform, pHandler)

    def close(self):
        """ Called when the AlexaAudio object is no longer needed. This closes the PyAudio instance.
        """
        # Terminate the pyaudio instance
        return
        self.pyaudio_instance.terminate()

    def get_audio(self, timeout=None):
        """ Get audio from the microphone. The SpeechRecognition package is used to automatically stop listening
            when the user stops speaking. A timeout can also be specified. If the timeout is reached, the function
            returns None.

            This function can also be used for debugging purposes to read an example audio file.

        :param timeout: timeout in seconds, when to give up if the user did not speak.
        :return: the raw binary audio string (PCM)
        """
        raw_audio = self.silence_listener()
        
        # Create a speech recognizer
        #r = speech_recognition.Recognizer()
        # Open the microphone (and release is when done using "with")
        #with speech_recognition.Microphone() as source:
        #    if timeout is None:
        #        # Prompt user to say something
        #       print("You can start talking now...")
        #        # TODO add sounds to prompt the user to do something, rather than text
        #        # Record audio until the user stops talking
        #        audio = r.listen(source)
        #    else:
        #        print("Start talking now, you have %d seconds" % timeout)
        ##        # TODO add sounds to prompt the user to do something, rather than text
        #        try:
        #            audio = r.listen(source, timeout=timeout)
        #        except speech_recognition.WaitTimeoutError:
        #            return None
        # Convert audio to raw_data (PCM)
        #raw_audio = audio.get_raw_data()

        # Rather than recording, read a pre-recorded example (for testing)
        #with open('files/example_get_time.pcm', 'rb') as f:
        #  raw_audio = f.read()
        return raw_audio

    def get_weather_request(self):
        with open('/opt/AlexaPi/src/files/weatherrequest.pcm', 'rb') as f:
            raw_audio = f.read()
        return raw_audio

    def silence_listener(self):
        VAD_SAMPLERATE = 16000
        VAD_FRAME_MS = 30
        VAD_PERIOD = (VAD_SAMPLERATE / 1000) * VAD_FRAME_MS
        VAD_SILENCE_TIMEOUT = 1000
        VAD_THROWAWAY_FRAMES = 10
        MAX_RECORDING_LENGTH = 8
        MAX_VOLUME = 100
        MIN_VOLUME = 30
        print("Debug: Setting up recording")
        vad = webrtcvad.Vad(2)
        # Reenable reading microphone raw data
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, 'plughw:1')
        inp.setchannels(1)
        inp.setrate(VAD_SAMPLERATE)
        inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        inp.setperiodsize(VAD_PERIOD)
        audio = ""

        # Buffer as long as we haven't heard enough silence or the total size is within max size
        thresholdSilenceMet = False
        frames = 0
        numSilenceRuns = 0
        silenceRun = 0
        start = time.time()

        print("Debug: Start recording")

        #platform.indicate_recording()

        # do not count first 10 frames when doing VAD
        while frames < VAD_THROWAWAY_FRAMES:  # VAD_THROWAWAY_FRAMES):
                length, data = inp.read()
                frames = frames + 1
                if length:
                        audio += data

        # now do VAD
        while ((thresholdSilenceMet is False) and ((time.time() - start) < MAX_RECORDING_LENGTH)):
                length, data = inp.read()
                if length:
                        audio += data

                        if length == VAD_PERIOD:
                                isSpeech = vad.is_speech(data, VAD_SAMPLERATE)

                                if not isSpeech:
                                        silenceRun = silenceRun + 1
                                        # print "0"
                                else:
                                        silenceRun = 0
                                        numSilenceRuns = numSilenceRuns + 1
                                        # print "1"

                # only count silence runs after the first one
                # (allow user to speak for total of max recording length if they haven't said anything yet)
                if (numSilenceRuns != 0) and ((silenceRun * VAD_FRAME_MS) > VAD_SILENCE_TIMEOUT):
                        thresholdSilenceMet = True

        #if debug:
        print("Debug: End recording")

        #platform.indicate_recording(False)
        #with open('/opt/AlexaPi/src/files/outstandingrequest.pcm', 'w') as rf:
        #        rf.write(audio)
        #inp.close()
        return audio


    def play_mp3(self, raw_audio):
        """ Play an MP3 file. Alexa uses the MP3 format for all audio responses. PyAudio does not support this, so
            the MP3 file must first be converted to a wave file before playing.

            This function assumes ffmpeg is located in the current working directory (ffmpeg/bin/ffmpeg).

        :param raw_audio: the raw audio as a binary string
        """
        # Save MP3 data to a file
        #time.sleep(2)
        #return
        with open("/opt/AlexaPi/src/files/response.mp3", 'wb') as f:
            f.write(raw_audio)
        media = self.vlc_instance.media_new("/opt/AlexaPi/src/files/response.mp3")
        self.player.set_media(media)
        self.player.play()
        # Convert mp3 response to wave (pyaudio doesn't work with MP3 files)
        #subprocess.call(['ffmpeg/bin/ffmpeg', '-y', '-i', 'files/response.mp3', 'files/response.wav'],
        #                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        # Play a wave file directly
        #self.play_wav('files/response.wav')

    def play_alexa_yes(self):
        media = self.vlc_instance.media_new("/opt/AlexaPi/src/files/alexayes.mp3")
        self.player.set_media(media)
        self.player.play()
        #time.sleep(.5)
    
    def play_alexa_outstanding(self):
        media = self.vlc_instance.media_new("/opt/AlexaPi/src/files/outstandingrequest.pcm")
        self.player.set_media(media)
        self.player.play()
        #time.sleep(.5)
    
    def play_beep(self):
        media = self.vlc_instance.media_new("/opt/AlexaPi/src/files/beep.wav")
        self.player.set_media(media)
        self.player.play()
        #time.sleep(.5)

    def play_alarm(self):
        media = self.vlc_instance.media_new("/opt/AlexaPi/src/files/alarm.wav")
        self.player.set_media(media)
        self.player.play()
        time.sleep(10)

    def play_wav(self, file, timeout=None, stop_event=None, repeat=False):
        """ Play a wave file using PyAudio. The file must be specified as a path.

        :param file: path to wave file
        """
        # Open wave wave
        return
        with wave.open(file, 'rb') as wf:
            # Create pyaudio stream
            stream = self.pyaudio_instance.open(
                        format=self.pyaudio_instance.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

            # Set chunk size for playback
            chunk = 1024

            # Get start time
            start_time = time.mktime(time.gmtime())

            end = False
            while not end:
                # Read first chunk of data
                data = wf.readframes(chunk)
                # Continue until there is no data left
                while len(data) > 0 and not end:
                    if timeout is not None and time.mktime(time.gmtime())-start_time > timeout:
                        end = True
                    if stop_event is not None and stop_event.is_set():
                        end = True
                    stream.write(data)
                    data = wf.readframes(chunk)
                if not repeat:
                    end = True
                else:
                    wf.rewind()

        # When done, stop stream and close
        stream.stop_stream()
        stream.close()
