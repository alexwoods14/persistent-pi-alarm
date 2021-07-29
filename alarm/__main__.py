from display import Display
import threading
from alarm import Alarm
import schedule
import time


def main():
    display = Display()
    threading.Thread(target=display.show_time).start()
    print("display running")
    schedule.every().day.at("09:00").do(job)
    print("alarm schedule set")
    while 1:
        schedule.run_pending()
        time.sleep(1)

def job():
    alarm = Alarm()



if __name__ == "__main__":
    print("entered")
    main()
