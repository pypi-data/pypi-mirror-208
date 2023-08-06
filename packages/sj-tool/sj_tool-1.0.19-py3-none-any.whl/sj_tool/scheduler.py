from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from sj_tool.decorator import singleton


@singleton
class Scheduler(object):
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def add_interval_job(self, job_fn, seconds, job_store="default", args=None) -> str:
        """
        添加定期执行的任务
        :param job_fn: 要运行的函数
        :param seconds: 间隔时间，单位：秒
        :param job_store: 用户可自定义的job空间，借助这个用户可以将job分类，加入到不同的jobstore，方便管理
        :param args: 要运行函数的参数
        :return:
        """
        # 注意：BlockingScheduler会阻塞当前线程，直到调度器被关闭。
        # 添加一个定时任务
        job = self.scheduler.add_job(job_fn, "interval", seconds=seconds, jobstore=job_store, args=args)
        return job.id

    def add_fix_time_job(self, job_fn, hour, minute=0, second=0, job_store="default", args=None) -> str:
        """
        添加定期执行的任务
        :param job_fn: 要运行的函数
        :param hour: 时
        :param minute: 分
        :param second: 秒
        :param job_store: 用户可自定义的job空间，借助这个用户可以将job分类，加入到不同的jobstore，方便管理
        :param args: 要运行函数的参数
        :return: str, job的id
        """
        # 注意：BlockingScheduler会阻塞当前线程，直到调度器被关闭。
        # 添加一个定时任务
        job = self.scheduler.add_job(
            job_fn, "cron", hour=hour, minute=minute, second=second, jobstore=job_store, args=args
        )
        return job.id

    def start(self):
        # 开始调度任务
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()

    def remove_jobs(self, job_store="default", job_id=None):
        if job_id is None:
            self.scheduler.remove_all_jobs(job_store)
        else:
            self.scheduler.remove_job(job_id, job_store)
