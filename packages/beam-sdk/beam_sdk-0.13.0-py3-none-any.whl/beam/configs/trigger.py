from typing import Dict, List, Optional, Union

from beam.base import AbstractDataLoader
from beam.serializer import (
    RestAPITrigger,
    CronJobTrigger,
    WebhookTrigger,
)
from beam.configs.autoscaling import AutoscalingManager
from beam.types import Types


class TriggerType:
    Webhook = "webhook"
    RestAPI = "rest_api"
    CronJob = "cron_job"


class TriggerManager(AbstractDataLoader):
    def __init__(self) -> None:
        self.webhooks: List[
            WebhookTrigger,
        ] = []
        self.cron_jobs: List[CronJobTrigger] = []
        self.rest_apis: List[RestAPITrigger] = []
        self.AutoScaling: AutoscalingManager = AutoscalingManager()

    def _validate_trigger_groupings(self):
        """
        NOTE: For the time being, the Beam APP can only accept one trigger during the alpha
        stages. Later we will allow multiple trigger types for webhooks (Slack, Twitter, etc)
        """
        triggers = self.webhooks + self.cron_jobs + self.rest_apis

        if len(triggers) > 1:
            raise ValueError("App can only have 1 trigger at a time")

    def Webhook(
        self,
        inputs: Dict[str, Types],
        handler: str,
        loader: Optional[str] = None,
        max_pending_tasks: Optional[int] = 1000,
        callback_url: Optional[str] = None,
        **_,
    ):
        """
        Arguments:
            handler: specify what method in which file to use as the entry point
            inputs: dictionary specifying how to serialize/deserialize input arguments
            max_pending_tasks (optional): maximum number of pending tasks in the queue, if exceeded, the webhook will prevent further items from being enqueued

        """
        self.webhooks.append(
            WebhookTrigger(
                inputs=inputs,
                handler=handler, 
                max_pending_tasks=max_pending_tasks, 
                loader=loader, 
                callback_url=callback_url
            )
        )
        self._validate_trigger_groupings()

    def Schedule(self, when: str, handler: str, **_):
        """
        Arguments:
            handler: specify what method in which file to use as the entry point
            when: CRON string to indicate the schedule in which the job is to run
                - https://en.wikipedia.org/wiki/Cron \
        """
        self.cron_jobs.append(
            CronJobTrigger(when=when, handler=handler),
        )
        self._validate_trigger_groupings()

    def RestAPI(
        self,
        inputs: Dict[str, Types],
        handler: str,
        outputs: Optional[Dict[str, Types]] = None,
        loader: Optional[str] = None,
        keep_warm_seconds: Optional[int] = None,
        **_,
    ):
        """
        Arguments:
            handler: specify what method in which file to use as the entry point
            loader: specify the method that will load the data into the handler (optional)
            inputs: dictionary specifying how to serialize/deserialize input arguments
            outputs: dictionary specifying how to serialize/deserialize return values
            keep_warm_seconds: how long the app should stay warm after the last request
        """
        self.rest_apis.append(
            RestAPITrigger(
                inputs=inputs,
                outputs=outputs,
                handler=handler,
                loader=loader,
                keep_warm_seconds=keep_warm_seconds,
            )
        )
        self._validate_trigger_groupings()

    def get_trigger(self) -> Union[RestAPITrigger, CronJobTrigger, WebhookTrigger]:
        self._validate_trigger_groupings()
        triggers = self.webhooks + self.cron_jobs + self.rest_apis

        if len(triggers) == 0:
            return None

        return triggers[0]

    def dumps(self):
        # To make this backwards compatible in the future after switching back to
        # multiple triggers, we will make this a list that currently will only have 1 trigger
        self._validate_trigger_groupings()
        triggers = []

        if len(self.webhooks) != 0:
            triggers.append(self.webhooks[0].validate_and_dump())
        elif len(self.cron_jobs) != 0:
            triggers.append(self.cron_jobs[0].validate_and_dump())
        elif len(self.rest_apis) != 0:
            triggers.append(self.rest_apis[0].validate_and_dump())

        return triggers

    def from_config(self, triggers):
        if triggers is None:
            return

        for t in triggers:
            trigger_type = t.get("trigger_type")
            inputs = {}
            outputs = {}

            if t.get("inputs") is not None:
                inputs = Types.load_schema(t.get("inputs"))

            if "inputs" in t:
                del t["inputs"]

            if t.get("outputs") is not None:
                outputs = Types.load_schema(t.get("outputs"))

            if "outputs" in t:
                del t["outputs"]

            if trigger_type == TriggerType.Webhook:
                self.Webhook(**t, inputs=inputs)
            elif trigger_type == TriggerType.CronJob:
                self.Schedule(**t)
            elif trigger_type == TriggerType.RestAPI:
                self.RestAPI(**t, inputs=inputs, outputs=outputs)
            else:
                raise ValueError(
                    f"Found an unknown trigger type in config: {trigger_type}"
                )
