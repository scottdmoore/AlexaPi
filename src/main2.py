
import helper
import authorization
import alexa_device

from pocketsphinx import get_model_path
from pocketsphinx.pocketsphinx import Decoder
import alsaaudio
import os
import sys
import tempfile
import time

import strandtest


__author__ = "NJC"
__license__ = "MIT"
__version__ = "0.2"

# constants
VAD_SAMPLERATE = 16000
VAD_FRAME_MS = 30
VAD_PERIOD = (VAD_SAMPLERATE / 1000) * VAD_FRAME_MS
VAD_SILENCE_TIMEOUT = 1000
VAD_THROWAWAY_FRAMES = 10
MAX_RECORDING_LENGTH = 8
MAX_VOLUME = 100
MIN_VOLUME = 30


def user_input_loop(alexa_device):
  """ This thread initializes a voice recognition event based on user input. This function uses command line
      input for interacting with the user. The user can start a recording, or quit if desired.
      This is currently the "main" thread for the device.
  """
  try:
    # While the stop event is not set
    #while True:
    #    # Prompt user to press enter to start a recording, or q to quit
    #    text = raw_input("Press enter anytime to start recording (or 'q' to quit).")
    #    # If 'q' is pressed
    #    if text == 'q':
    #        # Set stop event and break out of loop
    #        alexa_device.close()
    #        break
    #
    #    # If enter was pressed (and q was not)
    #    # Get raw audio from the microphone
    #    alexa_device.user_initiate_audio()
    #im = importlib.import_module('playback_handlers.vlchandler', package=None)
    #cl = getattr(im, 'VlcHandler')
    #pHandler = cl(config, playback_callback)
    #player = Player(config, platform, pHandler)

    # Setup
    recorded = False
    path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
    resources_path = os.path.join(path, 'resources', '')
    tmp_path = os.path.join(tempfile.mkdtemp(prefix='AlexaPi-runtime-'), '')

    # PocketSphinx configuration
    ps_config = Decoder.default_config()

    # Set recognition model to US
    ps_config.set_string('-hmm', os.path.join(get_model_path(), 'en-us'))
    ps_config.set_string('-dict', os.path.join(get_model_path(), 'cmudict-en-us.dict'))

    # Specify recognition key phrase
    #ps_config.set_string('-keyphrase', 'alexa')
    #ps_config.set_float('-kws_threshold', 1e-5)
    ps_config.set_string('-kws', '/opt/AlexaPi/src/gram')

    #hide Hide the VERY verbose logging information
    ps_config.set_string('-logfn', '/dev/null')

    # Process audio chunk by chunk. On keyword detected perform action and restart search
    decoder = Decoder(ps_config)
    decoder.start_utt()
    while True:
      record_audio = False

      # Enable reading microphone raw data
      inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, "plughw:1")
      inp.setchannels(1)
      inp.setrate(16000)
      inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
      inp.setperiodsize(1024)
      alexa_triggered = False
      lights_triggered = False
      darkness_triggered = False
      while not record_audio:
        print "Waiting for trigger words"
        time.sleep(.1)
        triggered = False
        test = ""
        # Process microphone audio via PocketSphinx, listening for trigger word
        while not triggered:
          # Read from microphone
          _, buf = inp.read()
          # Detect if keyword/trigger word was said
          decoder.process_raw(buf, False, False)
          #triggered_by_platform = platform.should_record()
          hypothesis = decoder.hyp()
          if hypothesis is not None:
              darkness_triggered = True
              test = hypothesis.hypstr
              print "Hype:" +test+":test"
              if str(test) == "alexa":
                  print "!!ALEXA"
                  alexa_triggered = True
              elif str(test) == "sunrise":
                  print "!!LIGHTS"
                  lights_triggered = True
              elif str(test) == "darkness":
                  print "!!DARK"
                  darkness_triggered = True
          triggered = lights_triggered or alexa_triggered or darkness_triggered

        #if player.is_playing():
        #  player.stop()
        print "Record audio is true"
        record_audio = True

        #if triggered_by_voice or (triggered_by_platform and platform.should_confirm_trigger):
        #  player.play_speech(resources_path + 'alexayes.mp3')

      # To avoid overflows close the microphone connection
      inp.close()

      # clean up the temp directory
      for some_file in os.listdir(tmp_path):
        file_path = os.path.join(tmp_path, some_file)
        try:
          if os.path.isfile(file_path):
            os.remove(file_path)
        except Exception as exp: # pylint: disable=broad-except
          print(exp)
      if alexa_triggered:
          print "HEARD ALEXA"
          alexa_device.user_initiate_audio()
      elif lights_triggered:
          print "SUNRISE!"
          alexa_device.start_sunrise(30)
      elif darkness_triggered:
          print "Dark!"
          alexa_device.stop_sunrise()
          strandtest.doDarkness()
      #silence_listener(VAD_THROWAWAY_FRAMES)
      #alexa_speech_recognizer()

      # Now that request is handled restart audio decoding
      decoder.end_utt()
      decoder.start_utt()
  except KeyboardInterrupt:
    alexa_device.close()
    print 'interrupted!'




#print "Starting in 10 seconds"
#time.sleep(10)
with open('/home/pi/sdm_alexa.log', 'w') as f:
    sys.stdout = f
    # Load configuration file (contains the authorization for the user and device information)
    config = helper.read_dict('/opt/AlexaPi/src/config.dict')
    # Check for authorization, if none, initialize and ask user to go to a website for authorization.
    if 'refresh_token' not in config:
        print("Please go to http://localhost:5000")
        authorization.get_authorization()
        config = helper.read_dict('/opt/AlexaPi/src/config.dict')
    # Create alexa device
    alexa_device = alexa_device.AlexaDevice(config)
    print "Device Started"
    user_input_loop(alexa_device)

    print("Done")
