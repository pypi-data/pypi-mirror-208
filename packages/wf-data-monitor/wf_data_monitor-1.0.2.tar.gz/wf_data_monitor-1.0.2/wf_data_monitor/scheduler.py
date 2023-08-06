import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import dateutil

from .const import UWB_UPLOAD_DELAY, VIDEO_UPLOAD_DELAY
from .honeycomb_db.handle import HoneycombDBHandle
from .honeycomb_service import HoneycombCachingClient
from .log import logger
from . import tasks


class Scheduler:
    def __init__(self):
        self.honeycomb_client = HoneycombCachingClient()
        self.honeycomb_handle = HoneycombDBHandle()

        self.coordinating_scheduler = BlockingScheduler()
        self.coordinating_scheduler.add_job(
            self.update_monitoring_tasks,
            trigger="interval",
            minutes=10,
            id="coordinating_scheduler",
            next_run_time=datetime.now(dateutil.tz.tzutc()),
            misfire_grace_time=5,
        )

        self.tasks_scheduler = BackgroundScheduler()

    def update_monitoring_tasks(self):
        logger.info("Updating monitoring tasks")
        environments: list = self.honeycomb_client.fetch_all_environments(output_format="list", use_cache=False)

        for environment in environments:
            if environment["timezone_name"] is None or environment["timezone_name"] == "":
                logger.warning(
                    f"Will not schedule data monitoring jobs against '{environment['name']}' ({environment['environment_id']}), environment has not specified a timezone"
                )
                continue

            if environment["name"] != "dahlia":
                logger.warning(f"Temporarily skipping {environment['name']}")
                continue

            # TODO: Fetch start/end times from Honeycomb
            logger.info(f"Scheduling tasks for {environment['name']}")
            tz = dateutil.tz.gettz(environment["timezone_name"])
            tz_aware_datetime = datetime.now(tz=tz)
            environment_start_datetime = datetime.combine(
                date=tz_aware_datetime.date(), time=datetime.strptime("07:30", "%H:%M").time(), tzinfo=tz
            )
            environment_end_datetime = datetime.combine(
                date=tz_aware_datetime.date(), time=datetime.strptime("17:30", "%H:%M").time(), tzinfo=tz
            )

            common_kwargs = {
                "environment_id": environment["environment_id"],
                "environment_name": environment["name"],
                "classroom_start_time": environment_start_datetime,
                "classroom_end_time": environment_end_datetime,
                "timezone": tz,
            }

            extra_job_args = {}
            DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
            if DEBUG:
                extra_job_args["next_run_time"] = datetime.now(dateutil.tz.tzutc())

            self.tasks_scheduler.add_job(
                tasks.verify_uwb_capture,
                id=f"{environment['name']}_verify_uwb_capture",
                trigger=CronTrigger(
                    minute="*/5",  # Execute every fifth minute
                    day_of_week="mon-fri",
                    start_date=environment_start_datetime,  # Allow Cron Jobs to only run during school capture window
                    end_date=environment_end_datetime + timedelta(minutes=UWB_UPLOAD_DELAY),
                ),
                replace_existing=True,
                coalesce=True,
                misfire_grace_time=5,
                kwargs={"honeycomb_handle": self.honeycomb_handle, "upload_delay": UWB_UPLOAD_DELAY, **common_kwargs},
                **extra_job_args,
            )

            self.tasks_scheduler.add_job(
                tasks.verify_video_capture,
                id=f"{environment['name']}_verify_video_capture",
                trigger=CronTrigger(
                    minute="*/5",  # Execute every fifth minute
                    day_of_week="mon-fri",
                    start_date=environment_start_datetime,  # Allow Cron Jobs to only run during school capture window
                    end_date=environment_end_datetime + timedelta(minutes=VIDEO_UPLOAD_DELAY),
                ),
                replace_existing=True,
                coalesce=True,
                misfire_grace_time=5,
                kwargs={"upload_delay": VIDEO_UPLOAD_DELAY, **common_kwargs},
                **extra_job_args,
            )

    def start(self):
        self.tasks_scheduler.start()
        self.coordinating_scheduler.start()
