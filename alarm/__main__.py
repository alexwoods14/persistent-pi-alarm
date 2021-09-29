from display import Display
import threading
from alarm import Alarm
import schedule
import time


def main():
    display = Display()
    threading.Thread(target=display.show_time).start()
    print("display running")
    schedule.every().day.at("08:00").do(job)
    print("alarm set")
    while 1:
        schedule.run_pending()
        time.sleep(1)

def job():
    print("alarm starting")
    alarm = Alarm()
    alarm.start_alarm()



if __name__ == "__main__":
    print("entered")
    main()
    #job()
