import dataclasses

from typing import List, Optional, Union
from marshmallow import validate
from marshmallow_dataclass import dataclass

from beam.types import PythonVersion, OutputType, MountType, AutoscalingType, GpuType
from beam.base import BaseSerializer, BaseTriggerSerializer
from beam.utils.parse import compose_cpu, compose_memory
from beam import validators


@dataclass
class AppSpecV1Configuration(BaseSerializer):
    name: str = validators.field(validate.Length(max=128))
    cpu: str = validators.field(validators.SerializerMethod(compose_cpu))
    gpu: str = validators.field(
        validate.OneOf(choices=[gpu[1] for gpu in GpuType.Types])
    )
    memory: str = validators.field(validators.SerializerMethod(compose_memory))
    python_version: str = validators.field(
        validate.OneOf(choices=[version[1] for version in PythonVersion.Types])
    )
    python_packages: Union[str, List[str]]
    workspace: str


@dataclass
class AppSpecV2Configuration(BaseSerializer):
    name: str = validators.field(validate.Length(max=128))
    cpu: str = validators.field(validators.SerializerMethod(compose_cpu))
    gpu: str = validators.field(
        validate.OneOf(choices=[gpu[1] for gpu in GpuType.Types])
    )
    memory: str = validators.field(validators.SerializerMethod(compose_memory))
    python_version: str = validators.field(
        validate.OneOf(choices=[version[1] for version in PythonVersion.Types])
    )
    python_packages: Union[str, List[str]]
    commands: Union[str, List[str]]
    workspace: str


@dataclass
class RestAPITrigger(BaseTriggerSerializer):
    inputs: validators.TypeSerializerDict(required=True)
    outputs: validators.TypeSerializerDict()
    handler: str = validators.field(validators.IsFileMethod())
    loader: Optional[str] = validators.field(validators.IsFileMethod())
    keep_warm_seconds: Optional[int]
    trigger_type: str = "rest_api"


@dataclass
class CronJobTrigger(BaseTriggerSerializer):
    when: str = validators.field(validators.IsValidCronOrEvery())
    handler: str = validators.field(validators.IsFileMethod())
    trigger_type: str = "cron_job"


@dataclass
class WebhookTrigger(BaseTriggerSerializer):
    inputs: validators.TypeSerializerDict(required=True)
    handler: str = validators.field(validators.IsFileMethod())
    loader: Optional[str] = validators.field(validators.IsFileMethod())
    callback_url: Optional[str] = validators.field(validators.IsValidURL())
    max_pending_tasks: Optional[int] = 1000
    trigger_type: str = "webhook"


@dataclass
class FileConfiguration(BaseSerializer):
    path: str
    name: str
    output_type: str = validators.field(
        validate.OneOf(choices=[version[1] for version in OutputType.Types])
    )


@dataclass
class VolumeConfiguration(BaseSerializer):
    name: str
    app_path: str
    mount_type: str = validators.field(
        validate.OneOf(choices=[t[1] for t in MountType.Types])
    )
    checksum: str = None
    local_path: str = None


@dataclass
class AutoscalingMaxRequestLatencyConfiguration(BaseSerializer):
    desired_latency: float
    max_replicas: int
    autoscaling_type: str = dataclasses.field(
        metadata={
            "validate": validate.OneOf(choices=[t[1] for t in AutoscalingType.Types])
        }
    )
