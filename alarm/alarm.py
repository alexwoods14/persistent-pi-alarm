import time
import threading
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from classifier import Classifier
import subprocess

class Alarm:
    def __init__(self):
        # set song to use
        # gTTS summary of day
        # initialize classifier and watchdog stuff
        self.classifier = Classifier()
        self.in_bed_status = []
        self.watchdog_setup()
    
        path = '.'
        my_observer = Observer()
        my_observer.schedule(self.my_event_handler, path, recursive=True)
        my_observer.start()

        # start timelapse, ignore first 2 images due to exposure setting
        tl_cmd = ['raspistill', '-t', str(30*60*1000), '-tl', '1000', '-ex',
                  'night', '-o', '.tmp_images/photo%03d.jpg']
        subprocess.Popen(tl_cmd)

        # start morning song for 30 sec, increasing volume
        # then alarm sound
        # when out of bed - Morning summary then stop sound
        # If back in bed, play alarm again on repeat
        # After 30 mins - clean up
        try:
            for i in range(30*60): # for 30 mins
                time.sleep(1)
        except KeyboardInterrupt:
            my_observer.stop()
            my_observer.join()

    def watchdog_setup(self):
        patterns = [".tmp_images/*"]
        ignore_patterns = None
        ignore_directories = None
        case_sensitive = True
        self.my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns,
                                            ignore_directories, case_sensitive)
        self.my_event_handler.on_moved = self.on_created


    def on_created(self, event):
        #x = threading.Thread(target=new_image, args=(event.dest_path,))
        #x.start()
        image_url = event.dest_path
        print(f"{image_url} created.")
        print(self.classifier.classify(image_url))
        subprocess.Popen(['rm', image_url])
        print(f"{image_url} deleted.")


if __name__ == "__main__":
    alarm = Alarm()
