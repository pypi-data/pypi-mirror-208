import os
from pathlib import Path

DEPLOYMENT_READY_PATH = "/workspace/READY"


def is_local():
    app_id = os.environ.get("APP_ID")
    app_task_name = os.environ.get("APP_TASK_NAME")

    if app_id is None or app_task_name is None:
        return True


def checkpoint():
    if is_local():
        return

    Path(DEPLOYMENT_READY_PATH).touch()
