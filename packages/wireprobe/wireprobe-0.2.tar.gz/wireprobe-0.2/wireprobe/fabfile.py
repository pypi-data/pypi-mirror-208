import os

from app.HealthCheck import HealthCheck
from invoke import Collection, task

@task
def run(c, settings="", log_level=30):
    """
    Run healthcheck
    :param c:
    :param settings:
    :param log_level:
    :return:
    """
    health_check = HealthCheck(settings_file=settings, log_level=log_level)
    health_check.check()


healthcheck = Collection('healthcheck')
healthcheck.add_task(run)
