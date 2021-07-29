import time
import threading
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from classifier import Classifier
import subprocess
import numpy as np

class Alarm:
    def __init__(self):
        # set song to use
        # gTTS summary of day
        # initialize classifier and watchdog stuff
        self.classifier = Classifier()
        self.in_bed_status = []
        self.watchdog_setup()
        self.classifier_threads = []

        # start timelapse, ignore first 2 images due to exposure setting
        tl_proc = self.timelapse_setup()

        # start morning song for 30 sec, increasing volume
        try:
            audio = SoundHandler()
            audio.play_song()
            threading.Thread(target=audio.vol_increasing).start()
        except:
            if audio is not None:
                audio.cleanup()
        
        # then alarm sound
        # when out of bed - Morning summary then stop sound
        # If back in bed, play alarm again on repeat
        # After 30 mins - clean up
        try:
            for i in range(30*60): # for 30 mins
                time.sleep(0.5)
                if len(self.in_bed_status) > 3 and np.sum(self.in_bed_status[-2:]) == 0:
                    audio.cleanup()
                    break
        except:
            self.my_observer.stop()
            self.my_observer.join()

        for thread in self.classifier_threads:
            thread.join()
        
        self.my_observer.stop()
        self.my_observer.join()
        tl_proc.terminate()
        # sleep to allow image classifier threads to end
        time.sleep(2)

    def watchdog_setup(self):
        patterns = [".tmp_images/*"]
        ignore_patterns = None
        ignore_directories = None
        case_sensitive = True
        self.my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns,
                                            ignore_directories, case_sensitive)
        self.my_event_handler.on_moved = self.on_created
        
        self.my_observer = Observer()
        self.my_observer.schedule(self.my_event_handler, '.', recursive=True)
        self.my_observer.start()


    def on_created(self, event):
        x = threading.Thread(target=self.classify_image, args=(event.dest_path,))
        self.classifier_threads.append(x)
        x.start()

    def classify_image(self, image_url):
        prob = self.classifier.classify(image_url)
        in_bed = prob[1] <= 0.9
        self.in_bed_status.append(in_bed)
        subprocess.Popen(['rm', image_url])
        print(f"{in_bed} : {prob}")

    def timelapse_setup(self):
        tl_cmd = ['raspistill', '-t', str(30*60*1000), '-tl', '1000', '-ex',
                  'night', '-w', '200', '-h', '150', '-o',
                  '.tmp_images/photo%03d.jpg']
        return(subprocess.Popen(tl_cmd, stderr=subprocess.DEVNULL))


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
            self.audio_proc = subprocess.Popen(['mpg123', self.song], stdout=subprocess.DEVNULL) 

    def play_tts(self):
        # vol = 75%
        subprocess.Popen(['amixer', '-c', '0', 'sset', 'Headphone', '--', '%ddB' %
               self.min_vol + (self.max_vol-self.min_vol)*0.75
              ], stdout=subprocess.DEVNULL)
        if self.tts is not None:
            self.audio_proc = subprocess.Popen(['mpg123', self.tts], stdout=subprocess.DEVNULL) 

    def set_tts(self):
        toSay = "Good afternoon. How are you?"
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



def test_audio():
    try:
        audio = SoundHandler()
        print("PLAYING")
        audio.play_song()
        print("THREADING")
        threading.Thread(target=audio.vol_increasing).start()
        print("WAITING")
        time.sleep(30)
        print("WAITED")
        print(audio.audio_proc.poll())
        audio.cleanup()
        print("KILLED")
    except:
        print("ERROR, EXITING NOW")
        if audio is not None:
            audio.cleanup()

if __name__ == "__main__":
    alarm = Alarm()
    # test_audio()

