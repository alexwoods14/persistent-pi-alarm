import time
from picamera import PiCamera
import threading
from classifier import Classifier
import subprocess
import numpy as np
from gtts import gTTS
from datetime import datetime, timedelta
from sound_handler import SoundHandler

class Alarm:
    def __init__(self):

        self.counter = 0;
        # set song to use
        # gTTS summary of day
        # initialize classifier and watchdog stuff
        self.classifier = Classifier()
        self.in_bed_status = []
        
        # set up camera, allow time for sensor to adjust to light level
        self.camera = PiCamera()
        self.camera.resolution = (128,96)
        time.sleep(2)

        # set up audio
        self.audio = SoundHandler()

    def start_alarm(self):
        # get the time and define when alarm should stop being on 'standby'
        alarm_start = datetime.now()
        alarm_end = alarm_start + timedelta(minutes=30)
        
        # play alarm song until out of bed or go to beeping
        self.play_music()

        # for 30 mins
        while datetime.now() < alarm_end:
            # if not in bed, stop audio, exit loop
            if not self.check_in_bed():
                self.audio.cleanup()
                break
            else:
                if not self.audio.playing_sound():
                    self.audio.play_beep()

        self.audio.set_tts()
        time.sleep(1)
        self.audio.play_tts()
        while self.audio.playing_sound():
            time.sleep(1)
        
        while datetime.now() < alarm_end:
            if not self.check_in_bed():
                self.audio.cleanup()
            else:
                if not self.audio.playing_sound():
                    self.audio.play_beep()
            
        self.cleanup()

    def cleanup(self):
        self.audio.cleanup()

    def check_in_bed(self):
        image = np.empty((96, 128, 3), dtype=np.uint8)
        self.camera.capture(image, 'rgb')

        result = self.classifier.classify(image)

        # return 1 if (likely) in bed, 0 otherwise
        #return result[0] >= 0.5
        if self.counter < 20:
            self.counter += 1
            print("Returning 1")
            return 1
        else:
            print("Returning 0")
            return 0


    def play_music(self):
        # start music, start thread to increase volume as time goes on
        try:
            self.audio.play_song()
            threading.Thread(target=self.audio.vol_increasing).start()
        except Exception as e:
            print(e)
            if self.audio is not None:
                self.audio.cleanup()


if __name__ == "__main__":
    alarm = Alarm()

    try:
        alarm.start_alarm()
    except Exception as e:
        print(e)
        if alarm.audio is not None:
            alarm.audio.cleanup()


