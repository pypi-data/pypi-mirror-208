import re
from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler


def shared_task(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


class Scheduler:
    scheduler = None

    def __init__(self):
        if Scheduler.scheduler:
            try:
                Scheduler.scheduler.shutdown(False)
                Scheduler.scheduler = BlockingScheduler()
            except Exception as e:
                print(e)
            pass
        else:
            Scheduler.scheduler = BlockingScheduler()

    @staticmethod
    def get_cron(corn_str):
        cron_list = re.split(r'\s+', corn_str.strip())
        cron_list += ["*"] * 7
        second = cron_list[0]
        minute = cron_list[1]
        hour = cron_list[2]
        day = cron_list[3]
        month = cron_list[4]
        day_of_week = '*' if cron_list[5] in ('?', '？') else cron_list[5]
        year = cron_list[6]
        return second, minute, hour, day, month, day_of_week, year

    def add_jobs(self, fun, schedules=None, cron=None):
        if cron:
            second, minute, hour, day, month, day_of_week, year = self.get_cron(cron)
            if schedules:
                Scheduler.scheduler.add_job(fun, 'cron', year=year, day_of_week=day_of_week, month=month, day=day,
                                            hour=hour, minute=minute, second=second, args=(schedules,))
            else:
                Scheduler.scheduler.add_job(fun, 'cron', year=year, day_of_week=day_of_week, month=month, day=day,
                                            hour=hour, minute=minute, second=second)
            return True
        elif schedules:
            for schedule in schedules:
                if schedule.cron and schedule.cron.strip():
                    try:
                        second, minute, hour, day, month, day_of_week, year = self.get_cron(schedule.cron.strip())
                        Scheduler.scheduler.add_job(fun, 'cron', year=year, day_of_week=day_of_week, month=month,
                                                    day=day, hour=hour, minute=minute, second=second, args=(schedule,))
                    except Exception as e:
                        print("Error:" + str(e))
        return True

    @staticmethod
    def start():
        Scheduler.scheduler.start()