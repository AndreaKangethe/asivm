from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import get_settings


def create_scheduler(scan_job, infer_job) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    settings = get_settings()
    scheduler.add_job(infer_job, "interval", seconds=settings.infer_interval_seconds, id="scheduled-inference")
    return scheduler
