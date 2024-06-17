import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from django_apscheduler.jobstores import register_events, register_job

from django.conf import settings

from django_apscheduler.jobstores import DjangoJobStore

# Create scheduler to run in a thread inside the application process
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)


def start():
    if settings.DEBUG:
        # Hook into the apscheduler logger
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    # Adding this job here instead of to crons.
    # This will do the following:
    # - Add a scheduled job to the job store on application initialization
    # - The job will execute a model class method at midnight each day
    # - replace_existing in combination with the unique ID prevents duplicate copies of the job
    # clear the job store to prevent duplicate copies of the job

    DjangoJobStore().remove_all_jobs()
    scheduler.add_job("esoteric_minds.tasks:set_star_user", "cron", id="set_star_user",
                      month="*/1", replace_existing=True)

    # Add the scheduled jobs to the Django admin interface
    register_events(scheduler)

    scheduler.start()
