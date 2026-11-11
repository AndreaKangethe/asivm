from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import get_settings


def create_scheduler(scan_job) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(scan_job, "interval", minutes=get_settings().scan_interval_minutes, id="scheduled-scan")
    return scheduler
