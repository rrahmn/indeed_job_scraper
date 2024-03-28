import schedule
import time
import datetime

from pipeline import main

def job():
    main()

def run_scheduler():
    # schedule the job every 15 minutes
    schedule.every(15).minutes.do(job)

    # first run at start of hour
    next_run = datetime.datetime.now() + datetime.timedelta(hours=1)
    next_run = next_run.replace(minute=0, second=0, microsecond=0)
    first_delay = (next_run - datetime.datetime.now()).total_seconds()
    time.sleep(first_delay)

    job()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()