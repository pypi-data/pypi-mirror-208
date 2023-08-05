from typing import Union

from beam.base import AbstractDataLoader
from beam.serializer import AutoscalingMaxRequestLatencyConfiguration
from beam.types import AutoscalingType


class AutoscalingManager(AbstractDataLoader):
    def __init__(self) -> None:
        self.autoscaling_config: Union[
            AutoscalingMaxRequestLatencyConfiguration, None
        ] = None

    def MaxRequestLatency(self, desired_latency: float, max_replicas: int, **_):
        """
        Arguments:
            desired_latency: maximum time (in seconds), you'd like to wait for a request to be processed
            max_replicas: maximum number of parallel workers spun up to handle incoming requests

        Note: MaxRequestLatency autoscaling only makes sense for asynchronous triggers (Webhook/Schedule)
        """
        self.autoscaling_config = AutoscalingMaxRequestLatencyConfiguration(
            desired_latency=desired_latency,
            max_replicas=max_replicas,
            autoscaling_type=AutoscalingType.MaxRequestLatency,
        )

    def dumps(self):
        if self.autoscaling_config is not None:
            return self.autoscaling_config.validate_and_dump()
        else:
            return {}

    def from_config(self, autoscaling_config: Union[dict, None]):
        if autoscaling_config is None:
            return

        if (
            autoscaling_config.get("autoscaling_type")
            == AutoscalingType.MaxRequestLatency
        ):
            self.MaxRequestLatency(**autoscaling_config)
