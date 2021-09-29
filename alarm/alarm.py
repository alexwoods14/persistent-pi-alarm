import time
import threading
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from classifier import Classifier
import subprocess
import numpy as np
from gtts import gTTS
from datetime import datetime, timedelta
from sound_handler import SoundHandler

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
        # give time for camera to set up
        while len(self.in_bed_status) < 50:
            time.sleep(1)
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=30)
        
        # play alarm song until out of bed
        try:
            audio = SoundHandler()
            #audio.play_song()
            #threading.Thread(target=audio.vol_increasing).start()
        except:
            if audio is not None:
                audio.cleanup()
        
        while len(self.in_bed_status) > 4 and np.sum(self.in_bed_status[-2:]) != 0:
            time.sleep(1)

        audio.cleanup()
        time.sleep(2)
        audio.set_tts()
        #audio.play_tts()
        while audio.audio_proc.poll() is None:
            time.sleep(1)
        audio.cleanup()
        try:
            for i in range(30*60): # for 30 mins
                time.sleep(0.8)
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
        in_bed = prob[1] <= 0.8
        self.in_bed_status.append(in_bed)
        subprocess.Popen(['rm', image_url])
        print(f"{in_bed} : {prob}")

    def timelapse_setup(self):
        tl_cmd = ['raspistill', '-t', str(30*60*1000), '-tl', '1000', '-ex',
                  'nightpreview', '-w', '128', '-h', '96', '-o',
                  '.tmp_images/photo%03d.jpg']
        return(subprocess.Popen(tl_cmd, stderr=subprocess.DEVNULL))


if __name__ == "__main__":
    alarm = Alarm()
    # test_audio()

