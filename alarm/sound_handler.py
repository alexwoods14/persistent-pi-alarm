import time
import subprocess
import numpy as np
from gtts import gTTS
from datetime import datetime 

class SoundHandler:
    def __init__(self):
        self.min_vol = -30
        self.max_vol = 4
        subprocess.Popen(['amixer', '-c', '0', 'sset', 'Headphone', '--', '%ddB' % self.min_vol], stdout=subprocess.DEVNULL)

        # decide song to play today
        self.song = "/home/pi/Music/starwars.mp3"
        self.audio_proc = None
        self.tts = None

    
    def play_song(self):
        # vol = min
        subprocess.Popen(['amixer', '-c', '0', 'sset', 'Headphone', '--', '%ddB' % self.min_vol], stdout=subprocess.DEVNULL)
        if self.song is not None:
            self.audio_proc = subprocess.Popen(['mpg123', '-o', 'pulse', self.song], stdout=subprocess.DEVNULL) 

    def play_tts(self):
        # vol = 50%
        subprocess.Popen(['amixer', '-c', '0', 'sset', 'Headphone', '--', '%ddB' %
               (self.min_vol + (self.max_vol-self.min_vol)*0.75)
              ], stdout=subprocess.DEVNULL)
        if self.tts is not None:
            self.audio_proc = subprocess.Popen(['mpg123', self.tts], stdout=subprocess.DEVNULL)
    
    def play_beep(self):
        vol = 0.75
        subprocess.Popen(['amixer', '-c', '0', 'sset', 'Headphone', '--', '%ddB' %
               (self.min_vol + (self.max_vol-self.min_vol)*vol)
              ], stdout=subprocess.DEVNULL)
        self.audio_proc = subprocess.Popen(['mpg123', '-o', 'pulse', '-q', '--loop', '-1', '/home/pi/Music/beep.mp3'], stdout=subprocess.DEVNULL)

    def set_tts(self):
        time_tts = datetime.now().strftime("%I:%M %p")
        date_tts = datetime.now().strftime("%A the %d(st/nd/rd/th) of %B")
        toSay = "Good morning. The time is " + time_tts
        speech = gTTS(text=toSay, lang='en')
        speech.save("tts.mp3")
        self.tts = "tts.mp3"

    def vol_set(self, vol):
        subprocess.Popen(['amixer', '-c', '0', 'sset', 'Headphone', '--', '%ddB' % vol], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def vol_increasing(self, start=0, end=100):
        start_vol = self.min_vol + (self.max_vol-self.min_vol)*start/100
        end_vol = self.min_vol + (self.max_vol-self.min_vol)*end/100
        step_vol = 0.5
        sleep_step = 30/((end_vol - start_vol)/step_vol) 
        
        for i in np.arange(start_vol, end_vol+1, step_vol):
            if self.audio_proc is not None and self.audio_proc.poll() is not None:
                break
            self.vol_set(i)
            time.sleep(sleep_step)

    def cleanup(self):
        if self.audio_proc is not None and self.audio_proc.poll() is None:
            self.audio_proc.terminate()
        self.audio_proc = None

    def playing_sound(self):
        return self.audio_proc is not None and self.audio_proc.poll() is None



def test_audio():
#    try:
    audio = SoundHandler()
    audio.set_tts()
    audio.play_tts()
    while audio.audio_proc.poll() is None:
        time.sleep(1)
    audio.cleanup()
#    except:
#        print("ERROR, EXITING NOW")
#        if audio is not None:
#            audio.cleanup()


def test_beep():
    audio = SoundHandler()
    audio.play_beep()
    try:
        while audio.audio_proc.poll() is None:
            time.sleep(1)
    except Exception as e:
        print(e)
        if audio is not None:
            audio.cleanup()


if __name__ == "__main__":
    # alarm = Alarm()
    test_beep()

