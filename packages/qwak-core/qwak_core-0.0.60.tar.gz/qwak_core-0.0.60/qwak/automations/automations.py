import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List

from _qwak_proto.qwak.automation.v1.action_pb2 import Action as ActionProto
from _qwak_proto.qwak.automation.v1.action_pb2 import (
    AdvancedDeploymentOptions,
    BuildAndDeployAction,
    BuildMetricCondition,
    BuildSpec,
)
from _qwak_proto.qwak.automation.v1.action_pb2 import CpuResources as CpuResourcesProto
from _qwak_proto.qwak.automation.v1.action_pb2 import (
    DeploymentCondition as DeploymentConditionProto,
)
from _qwak_proto.qwak.automation.v1.action_pb2 import (
    DeploymentSize,
    DeploymentSpec,
    GitModelSource,
)
from _qwak_proto.qwak.automation.v1.action_pb2 import GpuResources
from _qwak_proto.qwak.automation.v1.action_pb2 import GpuResources as GpuResourceProto
from _qwak_proto.qwak.automation.v1.action_pb2 import GpuType, MemoryUnit
from _qwak_proto.qwak.automation.v1.action_pb2 import Resources as ResourceProto
from _qwak_proto.qwak.automation.v1.auto_scaling_pb2 import (
    AGGREGATION_TYPE_AVERAGE,
    AGGREGATION_TYPE_MAX,
    AGGREGATION_TYPE_MIN,
    AGGREGATION_TYPE_SUM,
    METRIC_TYPE_CPU,
    METRIC_TYPE_LATENCY,
    METRIC_TYPE_MEMORY,
)
from _qwak_proto.qwak.automation.v1.auto_scaling_pb2 import (
    AutoScalingConfig as AutoScalingConfigProto,
)
from _qwak_proto.qwak.automation.v1.auto_scaling_pb2 import (
    AutoScalingPrometheusTrigger as AutoScalingPrometheusTriggerProto,
)
from _qwak_proto.qwak.automation.v1.auto_scaling_pb2 import QuerySpec
from _qwak_proto.qwak.automation.v1.auto_scaling_pb2 import (
    ScaleTrigger as ScaleTriggerProto,
)
from _qwak_proto.qwak.automation.v1.auto_scaling_pb2 import Triggers as TriggersProto
from _qwak_proto.qwak.automation.v1.automation_pb2 import Automation as AutomationProto
from _qwak_proto.qwak.automation.v1.automation_pb2 import (
    AutomationAudit as AutomationAuditProto,
)
from _qwak_proto.qwak.automation.v1.automation_pb2 import (
    AutomationSpec as AutomationSpecProto,
)
from _qwak_proto.qwak.automation.v1.common_pb2 import Metric as MetricProto
from _qwak_proto.qwak.automation.v1.common_pb2 import MetricThresholdDirection
from _qwak_proto.qwak.automation.v1.common_pb2 import SqlMetric as SqlMetricProto
from _qwak_proto.qwak.automation.v1.notification_pb2 import (
    CustomWebhook as CustomWebhookProto,
)
from _qwak_proto.qwak.automation.v1.notification_pb2 import (
    HttpMethodType as HttpMethodTypeProto,
)
from _qwak_proto.qwak.automation.v1.notification_pb2 import (
    Notification as NotificationProto,
)
from _qwak_proto.qwak.automation.v1.notification_pb2 import (
    PostSlackNotification as PostSlackNotificationProto,
)
from _qwak_proto.qwak.automation.v1.trigger_pb2 import (
    MetricBasedTrigger as MetricBasedTriggerProto,
)
from _qwak_proto.qwak.automation.v1.trigger_pb2 import NoneTrigger as NoneTriggerProto
from _qwak_proto.qwak.automation.v1.trigger_pb2 import (
    OnBoardingTrigger as OnBoardingTriggerProto,
)
from _qwak_proto.qwak.automation.v1.trigger_pb2 import (
    ScheduledTrigger as ScheduledTriggerProto,
)
from _qwak_proto.qwak.automation.v1.trigger_pb2 import Trigger as TriggerProto
from google.protobuf.timestamp_pb2 import Timestamp


class ThresholdDirection(Enum):
    ABOVE = 1
    BELOW = 2


threshold_to_proto_mapping = {
    ThresholdDirection.ABOVE: MetricThresholdDirection.ABOVE,
    ThresholdDirection.BELOW: MetricThresholdDirection.BELOW,
}

proto_threshold_to_threshold = {v: k for k, v in threshold_to_proto_mapping.items()}


def map_threshold_direction_to_proto(
    direction: ThresholdDirection,
) -> MetricThresholdDirection:
    return threshold_to_proto_mapping.get(
        direction, MetricThresholdDirection.INVALID_METRIC_DIRECTION
    )


def map_proto_threshold_to_direction(
    direction: MetricThresholdDirection,
) -> ThresholdDirection:
    return proto_threshold_to_threshold.get(direction)


def map_memory_units(memory):
    memory_unit = re.sub(r"\d+", "", memory)
    if memory_unit == "Gi":
        return MemoryUnit.GIB
    elif memory_unit == "Mib":
        return MemoryUnit.MIB
    else:
        return MemoryUnit.UNKNOWN


def map_memory_units_proto(memory_unit: MemoryUnit):
    if memory_unit == MemoryUnit.MIB:
        return "Mib"
    elif memory_unit == MemoryUnit.GIB:
        return "Gi"
    else:
        return ""


@dataclass
class Trigger(ABC):
    def to_proto(self):
        # abstract method
        pass

    @staticmethod
    @abstractmethod
    def from_proto(message: TriggerProto):
        # abstract method
        pass


@dataclass
class Metric(ABC):
    @abstractmethod
    def to_proto(self):
        # abstract method
        pass

    @staticmethod
    @abstractmethod
    def from_proto(message: MetricProto):
        # abstract method
        pass


@dataclass
class ScheduledTrigger(Trigger):
    cron: str = field(default="")
    interval: str = field(default="")

    def to_proto(self):
        return (
            TriggerProto(
                scheduled_trigger=ScheduledTriggerProto(interval=self.interval)
            )
            if self.interval
            else TriggerProto(scheduled_trigger=ScheduledTriggerProto(cron=self.cron))
        )

    @staticmethod
    def from_proto(message: TriggerProto):
        return ScheduledTrigger(
            cron=message.scheduled_trigger.cron,
            interval=message.scheduled_trigger.interval,
        )


@dataclass
class MetricBasedTrigger(Trigger):
    name: str = field(default="")
    metric: Metric = field(default="")
    direction: ThresholdDirection = field(default=ThresholdDirection.ABOVE)
    threshold: str = field(default="")
    override_cron: str = field(default="")

    def to_proto(self):
        return TriggerProto(
            metric_based_trigger=MetricBasedTriggerProto(
                name=self.name,
                threshold=self.threshold,
                metric=self.metric.to_proto(),
                threshold_direction=map_threshold_direction_to_proto(self.direction),
                override_cron=self.override_cron,
            )
        )

    @staticmethod
    def from_proto(message: TriggerProto):
        metric = map_metric_name_to_class(
            message.metric_based_trigger.metric.WhichOneof("metric")
        )
        return MetricBasedTrigger(
            name=message.metric_based_trigger.name,
            metric=metric.from_proto(message.metric_based_trigger.metric)
            if metric
            else None,
            threshold=message.metric_based_trigger.threshold,
            direction=map_proto_threshold_to_direction(
                message.metric_based_trigger.threshold_direction
            ),
            override_cron=message.metric_based_trigger.override_cron,
        )


@dataclass
class NoneTrigger(Trigger):
    def to_proto(self):
        return TriggerProto(none_trigger=NoneTriggerProto())

    @staticmethod
    def from_proto(message: TriggerProto):
        return NoneTrigger()


@dataclass
class OnBoardingTrigger(Trigger):
    def to_proto(self):
        return TriggerProto(on_boarding_trigger=OnBoardingTriggerProto())

    @staticmethod
    def from_proto(message: TriggerProto):
        return OnBoardingTrigger()


@dataclass
class SqlMetric(Metric):
    sql_query: str = field(default="")

    def to_proto(self):
        return MetricProto(sql_metric=SqlMetricProto(sql_query=self.sql_query))

    @staticmethod
    def from_proto(message: MetricProto):
        return SqlMetric(sql_query=message.sql_metric.sql_query)


@dataclass
class Notification(ABC):
    def to_proto(self):
        # abstract method
        pass

    @staticmethod
    @abstractmethod
    def from_proto(message: TriggerProto):
        # abstract method
        pass


@dataclass
class SlackNotification(Notification):
    webhook: str = field(default="")

    def to_proto(self):
        return NotificationProto(
            post_slack_notification=PostSlackNotificationProto(
                webhook=self.webhook,
            )
        )

    @staticmethod
    def from_proto(message: NotificationProto):
        return SlackNotification(
            webhook=message.post_slack_notification.webhook,
        )

    def __str__(self):
        return f"Slack Notification:\n webhook:{self.webhook}\n"


@dataclass
class CustomWebhook(Notification):
    url: str = field(default="")
    http_method: str = field(default="GET")
    headers: Dict[str, str] = field(default_factory=dict)
    data: Dict[str, str] = field(default_factory=dict)

    _HTTP_NAME_TO_STATUS_MAPPING = {
        "GET": HttpMethodTypeProto.HTTP_METHOD_TYPE_GET,
        "POST": HttpMethodTypeProto.HTTP_METHOD_TYPE_POST,
        "PUT": HttpMethodTypeProto.HTTP_METHOD_TYPE_PUT,
        "PATCH": HttpMethodTypeProto.HTTP_METHOD_TYPE_PATCH,
        "DELETE": HttpMethodTypeProto.HTTP_METHOD_TYPE_DELETE,
        "HEAD": HttpMethodTypeProto.HTTP_METHOD_TYPE_HEAD,
    }

    _HTTP_STATUS_TO_NAME_MAPPING = {
        v: k for k, v in _HTTP_NAME_TO_STATUS_MAPPING.items()
    }

    def __post_init__(self):
        if self.http_method.upper() not in self._HTTP_NAME_TO_STATUS_MAPPING.keys():
            raise ValueError(
                f"HTTP method {self.http_method} is not a valid method. Available options are "
                f"{list(self._HTTP_NAME_TO_STATUS_MAPPING.keys())}"
            )

    def to_proto(self):
        return NotificationProto(
            custom_webhook=CustomWebhookProto(
                url=self.url,
                http_method=self._HTTP_NAME_TO_STATUS_MAPPING.get(
                    self.http_method.upper()
                ),
                headers=self.headers,
                data=self.data,
            )
        )

    @staticmethod
    def from_proto(message: NotificationProto):
        return CustomWebhook(
            url=message.custom_webhook.url,
            data=message.custom_webhook.data,
            headers=message.custom_webhook.headers,
            http_method=CustomWebhook._HTTP_STATUS_TO_NAME_MAPPING.get(
                message.custom_webhook.http_method
            ),
        )

    def __str__(self):
        return f"Custom webhook:\n url:{self.url}\n data:{self.data}\n headers:{self.headers}\n http method:{self.http_method}\n"


class MetricType(Enum):
    cpu = METRIC_TYPE_CPU
    latency = METRIC_TYPE_LATENCY
    memory = METRIC_TYPE_MEMORY


class AggregationType(Enum):
    avg = AGGREGATION_TYPE_AVERAGE
    max = AGGREGATION_TYPE_MAX
    min = AGGREGATION_TYPE_MIN
    sum = AGGREGATION_TYPE_SUM


@dataclass
class Action(ABC):
    @abstractmethod
    def to_proto(self):
        # abstract method
        pass

    @staticmethod
    @abstractmethod
    def from_proto(message: ActionProto):
        # abstract method
        pass


@dataclass
class DeploymentCondition(ABC):
    @abstractmethod
    def to_proto(self):
        # abstract method
        pass

    @staticmethod
    @abstractmethod
    def from_proto(message: DeploymentConditionProto):
        # abstract method
        pass


@dataclass
class AutoScaleTrigger(ABC):
    @abstractmethod
    def to_proto(self):
        # abstract method
        pass

    @staticmethod
    @abstractmethod
    def from_proto(message: ScaleTriggerProto):
        # abstract method
        pass


@dataclass
class BuildMetric(DeploymentCondition):
    metric_name: str = field(default="")
    direction: ThresholdDirection = field(default=ThresholdDirection.ABOVE)
    threshold: str = field(default="")

    def to_proto(self):
        return DeploymentConditionProto(
            build_metric=BuildMetricCondition(
                metric_name=self.metric_name,
                threshold=self.threshold,
                threshold_direction=map_threshold_direction_to_proto(self.direction),
            )
        )

    @staticmethod
    def from_proto(message: DeploymentConditionProto):
        return BuildMetric(
            metric_name=message.build_metric.metric_name,
            threshold=message.build_metric.threshold,
            direction=map_proto_threshold_to_direction(
                message.build_metric.threshold_direction
            ),
        )

    def __str__(self):
        return f"Metric Name: {self.metric_name}\tThreshold: {self.threshold}\tDirection: {self.direction.name}"


@dataclass
class Resources(ABC):
    @abstractmethod
    def to_proto(self):
        # abstract method
        pass

    @staticmethod
    @abstractmethod
    def from_proto(message: ResourceProto):
        # abstract method
        pass


@dataclass
class CpuResources(Resources):
    cpu_fraction: float = field(default=2)
    memory: str = field(default="2Gi")

    def to_proto(self):
        return ResourceProto(
            cpu_resources=CpuResourcesProto(
                cpu=self.cpu_fraction,
                memory_units=map_memory_units(memory=self.memory),
                memory_amount=int(
                    re.sub(
                        r"\D",
                        "",
                        self.memory,
                    )
                ),
            )
        )

    @staticmethod
    def from_proto(message: ResourceProto):
        return CpuResources(
            cpu_fraction=message.cpu_resources.cpu,
            memory=str(message.cpu_resources.memory_amount)
            + map_memory_units_proto(message.cpu_resources.memory_units),
        )

    def __str__(self):
        return f"CPU: {self.cpu_fraction}, Memory: {self.memory}"


@dataclass
class GpuResources(Resources):
    gpu_type: str = field(default=None)
    gpu_amount: str = field(default=None)

    def to_proto(self):
        return ResourceProto(
            gpu_resources=GpuResourceProto(
                gpu_type=self.gpu_type,
                gpu_amount=int(self.gpu_amount),
            )
        )

    def to_gpu_proto(self):
        return GpuResourceProto(
            gpu_type=self.gpu_type,
            gpu_amount=int(self.gpu_amount),
        )

    @staticmethod
    def from_proto(message: ResourceProto):
        return GpuResources(
            gpu_type=GpuType.Name(message.gpu_resources.gpu_type),
            gpu_amount=str(message.gpu_resources.gpu_amount),
        )

    @staticmethod
    def from_gpu_proto(message: GpuResources):
        return GpuResources(
            gpu_type=GpuType.Name(message.gpu_type),
            gpu_amount=str(message.gpu_amount),
        )

    def __str__(self):
        return f"GPU Type: {self.gpu_type}, GPU Amount: {self.gpu_amount}"


@dataclass
class AutomationAudit(ABC):
    date: datetime = field(default=datetime.now())
    user_id: str = field(default="")

    def to_proto(self):
        timestamp = Timestamp()
        timestamp.FromDatetime(self.date)
        return AutomationAuditProto(user_id=self.user_id, date=timestamp)

    @staticmethod
    def from_proto(message: AutomationAuditProto):
        return AutomationAudit(
            user_id=message.user_id,
            date=datetime.fromtimestamp(
                message.date.seconds + message.date.nanos / 1e9
            ),
        )


@dataclass
class BuildSpecifications:
    parameters: Dict[str, str] = field(default_factory=dict)
    git_uri: str = field(default=None)
    tags: List[str] = field(default_factory=list)
    git_access_token_secret: str = field(default=None)
    git_branch: str = field(default="main")
    main_dir: str = field(default="main")
    base_image: str = field(default="")
    assumed_iam_role: str = field(default="")
    resources: Resources = field(default=CpuResources())
    dependency_file_path: str = field(default=None)
    env_vars: List[str] = field(default_factory=list)

    def to_proto(self):
        return BuildSpec(
            parameters=self.parameters,
            git_model_source=GitModelSource(
                git_uri=self.git_uri,
                git_credentials_secret_name=self.git_access_token_secret,
                git_branch=self.git_branch,
            ),
            main_dir=self.main_dir,
            tags=self.tags,
            resource=self.resources.to_proto(),
            base_image=self.base_image,
            assumed_iam_role=self.assumed_iam_role,
            dependency_file_path=self.dependency_file_path,
            env_vars=self.env_vars,
        )

    @staticmethod
    def from_proto(build_spec: BuildSpec):
        resources = map_resources_name_to_class(
            build_spec.resource.WhichOneof("resource")
        )
        return BuildSpecifications(
            parameters=build_spec.parameters,
            git_uri=build_spec.git_model_source.git_uri,
            git_access_token_secret=build_spec.git_model_source.git_credentials_secret_name,
            git_branch=build_spec.git_model_source.git_branch,
            tags=build_spec.tags,
            main_dir=build_spec.main_dir,
            base_image=build_spec.base_image,
            resources=resources.from_proto(build_spec.resource) if resources else None,
            dependency_file_path=build_spec.dependency_file_path,
            assumed_iam_role=build_spec.assumed_iam_role,
            env_vars=build_spec.env_vars,
        )

    def __str__(self):
        result = f"Git Uri:\t{self.git_uri}\n"
        result += f"Git Branch:\t{self.git_branch}\n"
        result += (
            f"Git Access Token Secret:\t{self.git_access_token_secret}\n"
            if self.git_access_token_secret
            else ""
        )
        result += f"Main Dir:\t{self.main_dir}\n" if self.main_dir != "main" else ""
        result += f"Parameters:\t{self.parameters}\n" if self.parameters else ""
        result += f"Tags:\t{self.tags}\n" if self.tags else ""
        result += (
            f"IAM Role:\t{self.assumed_iam_role}\n" if self.assumed_iam_role else ""
        )
        result += f"Base Image:\t{self.base_image}\n" if self.base_image else ""
        result += f"Resources:\n{self.resources}\n" if self.resources else ""
        result += f"Environment Variables:\n{self.env_vars}\n" if self.env_vars else ""
        return result


@dataclass
class AutoScalingConfig:
    min_replica_count: int = field(default=None)
    max_replica_count: int = field(default=None)
    polling_interval: int = field(default=None)
    cool_down_period: int = field(default=None)
    triggers: List[AutoScaleTrigger] = field(default_factory=list)

    def to_proto(self):
        return AutoScalingConfigProto(
            min_replica_count=self.min_replica_count,
            max_replica_count=self.max_replica_count,
            polling_interval=self.polling_interval,
            cool_down_period=self.cool_down_period,
            triggers=TriggersProto(
                triggers=[trigger.to_proto() for trigger in self.triggers]
            ),
        )

    @staticmethod
    def from_proto(message: AutoScalingConfigProto):
        triggers = [
            map_autoscaling_trigger_name_to_class(
                trigger.WhichOneof("trigger_type")
            ).from_proto(trigger)
            for trigger in message.triggers.triggers
        ]
        return AutoScalingConfig(
            min_replica_count=message.min_replica_count,
            max_replica_count=message.max_replica_count,
            polling_interval=message.polling_interval,
            cool_down_period=message.cool_down_period,
            triggers=triggers,
        )

    def __str__(self):
        result = f"min replica count: {self.min_replica_count} \t max replica count: {self.max_replica_count} \t polling interval: {self.polling_interval} \t cool down period: {self.cool_down_period} \n"
        result += "Scale triggers: "
        for trigger in self.triggers:
            result += f" {trigger}"
        return result


@dataclass
class DeploymentSpecifications:
    number_of_http_server_workers: int = field(default=2)
    http_request_timeout_ms: int = field(default=5000)
    max_batch_size: int = field(default=1)
    daemon_mode: bool = field(default=False)
    variation_name: str = field(default="default")
    custom_iam_role_arn: str = field(default="")
    number_of_pods: int = field(default=2)
    cpu_fraction: float = field(default=2)
    memory: str = field(default="2Gi")
    gpu_resources: GpuResources = field(default=None)
    auto_scale_config: AutoScalingConfig = field(default=AutoScalingConfig())
    environments: List[str] = field(default_factory=list)
    env_vars: List[str] = field(default_factory=list)
    deployment_timeout: int = field(default=0)

    def to_proto(self):
        return DeploymentSpec(
            selected_variation_name=self.variation_name,
            deployment_size=DeploymentSize(
                number_of_pods=self.number_of_pods,
                cpu=self.cpu_fraction,
                memory_units=map_memory_units(memory=self.memory),
                memory_amount=int(
                    re.sub(
                        r"\D",
                        "",
                        self.memory,
                    )
                ),
                gpu_resources=self.gpu_resources.to_gpu_proto()
                if self.gpu_resources
                else None,
            ),
            advanced_options=AdvancedDeploymentOptions(
                number_of_http_server_workers=self.number_of_http_server_workers,
                http_request_timeout_ms=self.http_request_timeout_ms,
                max_batch_size=self.max_batch_size,
                daemon_mode=self.daemon_mode,
                custom_iam_role_arn=self.custom_iam_role_arn,
                auto_scaling_config=self.auto_scale_config.to_proto(),
                deployment_process_timeout_limit=self.deployment_timeout,
            ),
            environments=self.environments,
            env_vars=self.env_vars,
        )

    @staticmethod
    def from_proto(message: DeploymentSpec):
        return DeploymentSpecifications(
            variation_name=message.selected_variation_name,
            number_of_http_server_workers=message.advanced_options.number_of_http_server_workers,
            http_request_timeout_ms=message.advanced_options.http_request_timeout_ms,
            max_batch_size=message.advanced_options.max_batch_size,
            daemon_mode=message.advanced_options.daemon_mode,
            custom_iam_role_arn=message.advanced_options.custom_iam_role_arn,
            number_of_pods=message.deployment_size.number_of_pods,
            cpu_fraction=message.deployment_size.cpu,
            memory=str(message.deployment_size.memory_amount)
            + map_memory_units_proto(message.deployment_size.memory_units),
            gpu_resources=GpuResources.from_gpu_proto(
                message.deployment_size.gpu_resources
            )
            if message.deployment_size.gpu_resources
            else None,
            auto_scale_config=AutoScalingConfig.from_proto(
                message.advanced_options.auto_scaling_config
            ),
            environments=message.environments,
            env_vars=message.env_vars,
            deployment_timeout=message.advanced_options.deployment_process_timeout_limit,
        )

    def __str__(self):
        result = f"Number of Pods: {self.number_of_pods}\tCPU: {self.cpu_fraction}\tMemory: {self.memory}\tGPU: {self.gpu_resources}\n"
        result += (
            f"Number of HTTP Workers: {self.number_of_http_server_workers}\t"
            f"HTTP Request Timeout: {self.http_request_timeout_ms}\t"
            f"Daemon Mode: {self.daemon_mode}\t"
            f"Max Batch Size: {self.max_batch_size}\n"
        )
        result += f"Environment Variables: {self.env_vars}\n"
        result += (
            f"Custom IAM Role: {self.custom_iam_role_arn}"
            if self.custom_iam_role_arn
            else ""
        )
        result += f"Auto scaling config: {self.auto_scale_config}"
        return result


@dataclass
class QwakBuildDeploy(Action):
    build_spec: BuildSpecifications
    deployment_condition: DeploymentCondition
    deployment_spec: DeploymentSpecifications

    def to_proto(self):
        return ActionProto(
            build_deploy=BuildAndDeployAction(
                build_spec=self.build_spec.to_proto(),
                deployment_spec=self.deployment_spec.to_proto(),
                deployment_condition=self.deployment_condition.to_proto(),
            )
        )

    @staticmethod
    def from_proto(message: ActionProto):
        deployment_condition = map_deployment_condition_name_to_class(
            message.build_deploy.deployment_condition.WhichOneof("condition")
        )
        return QwakBuildDeploy(
            build_spec=BuildSpecifications.from_proto(message.build_deploy.build_spec),
            deployment_spec=DeploymentSpecifications.from_proto(
                message.build_deploy.deployment_spec
            ),
            deployment_condition=deployment_condition.from_proto(
                message.build_deploy.deployment_condition
            )
            if deployment_condition
            else None,
        )

    def __str__(self):
        return f"Build Specifications:\n{self.build_spec}\nDeployment Specification:\n{self.deployment_spec}\nDeployment Condition:\n{self.deployment_condition}"


@dataclass
class AutoScaleQuerySpec:
    metric_type: str = field(default=None)
    aggregation_type: str = field(default=None)
    time_period: int = field(default=None)

    def to_proto(self):
        return QuerySpec(
            time_period=self.time_period,
            metric_type=MetricType[self.metric_type.lower()].value,
            aggregation_type=AggregationType[self.aggregation_type.lower()].value,
        )

    @staticmethod
    def from_proto(message: QuerySpec):
        return AutoScaleQuerySpec(
            metric_type=map_auto_scaling_metric_type_proto_to_name(message.metric_type),
            aggregation_type=map_aggregation_type_proto_to_name(
                message.aggregation_type
            ),
            time_period=message.time_period,
        )

    def __str__(self):
        return f"metric type: {self.metric_type}\taggregation type: {self.aggregation_type}\ttime period: {self.time_period}"


@dataclass
class AutoScalingPrometheusTrigger(AutoScaleTrigger):
    query_spec: AutoScaleQuerySpec = field(default=QuerySpec)
    threshold: int = field(default=None)

    def to_proto(self):
        return ScaleTriggerProto(
            prometheus_trigger=AutoScalingPrometheusTriggerProto(
                query_spec=self.query_spec.to_proto(), threshold=self.threshold
            )
        )

    @staticmethod
    def from_proto(message: ScaleTriggerProto):
        return AutoScalingPrometheusTrigger(
            threshold=message.prometheus_trigger.threshold,
            query_spec=AutoScaleQuerySpec.from_proto(
                message.prometheus_trigger.query_spec
            ),
        )

    def __str__(self):
        return f"threshold: {self.threshold} \t {self.query_spec}"


@dataclass
class Automation:
    id: str = field(default="")
    name: str = field(default="")
    model_id: str = field(default="")
    execute_immediately: bool = field(default=False)
    trigger: Trigger = field(default_factory=Trigger)
    action: Action = field(default_factory=Action)
    description: str = field(default="")
    environment: str = field(default="")
    is_enabled: bool = field(default=True)
    is_deleted: bool = field(default=False)
    is_sdk_v1: bool = field(default=False)
    create_audit: AutomationAudit = field(default_factory=AutomationAudit)
    on_error: Notification = field(default=None)
    on_success: Notification = field(default=None)

    def to_proto(self):
        return AutomationProto(
            automation_id=self.id,
            automation_spec=AutomationSpecProto(
                automation_name=self.name,
                is_enabled=self.is_enabled,
                is_sdk_v1=self.is_sdk_v1,
                execute_immediately=self.execute_immediately,
                model_id=self.model_id,
                action=self.action.to_proto(),
                trigger=self.trigger.to_proto() if self.trigger is not None else None,
                on_error=self.on_error.to_proto()
                if self.on_error is not None
                else None,
                on_success=self.on_success.to_proto()
                if self.on_success is not None
                else None,
            ),
            qwak_environment_id=self.environment,
            create_audit=self.create_audit.to_proto(),
            is_deleted=self.is_deleted,
        )

    @staticmethod
    def from_proto(message: AutomationProto):
        action = map_action_name_to_class(
            message.automation_spec.action.WhichOneof("action")
        )
        trigger = map_trigger_name_to_class(
            message.automation_spec.trigger.WhichOneof("trigger")
        )
        on_error_notification = map_notification_name_to_class(
            message.automation_spec.on_error.WhichOneof("notification")
        )
        on_success_notification = map_notification_name_to_class(
            message.automation_spec.on_success.WhichOneof("notification")
        )

        return Automation(
            id=message.automation_id,
            name=message.automation_spec.automation_name,
            description=message.automation_spec.automation_description,
            execute_immediately=message.automation_spec.execute_immediately,
            model_id=message.automation_spec.model_id,
            is_enabled=message.automation_spec.is_enabled,
            is_sdk_v1=message.automation_spec.is_sdk_v1,
            is_deleted=message.is_deleted,
            action=action.from_proto(message.automation_spec.action)
            if action
            else None,
            trigger=trigger.from_proto(message.automation_spec.trigger)
            if trigger
            else None,
            environment=message.qwak_environment_id,
            create_audit=AutomationAudit.from_proto(message.create_audit),
            on_error=on_error_notification.from_proto(message.automation_spec.on_error)
            if on_error_notification
            else None,
            on_success=on_success_notification.from_proto(
                message.automation_spec.on_success
            )
            if on_success_notification
            else None,
        )

    def __str__(self):
        on_error = f"\nOn Error: {self.on_error}" if self.on_error else ""
        on_success = f"\nOn Success: {self.on_success}" if self.on_success else ""
        return f"Id: {self.id}\tName: {self.name}\tModel: {self.model_id}\nDescription: {self.description}\nAction: {self.action}\nTrigger: {self.trigger}{on_error}{on_success}"


def map_notification_name_to_class(notification_name: str):
    mapping = {
        "post_slack_notification": SlackNotification,
        "custom_webhook": CustomWebhook,
    }
    return mapping.get(notification_name)


def map_action_name_to_class(action_name: str):
    mapping = {"build_deploy": QwakBuildDeploy}
    return mapping.get(action_name)


def map_autoscaling_trigger_name_to_class(auto_scaling_trigger_name: str):
    mapping = {"prometheus_trigger": AutoScalingPrometheusTrigger}
    return mapping.get(auto_scaling_trigger_name)


def map_trigger_name_to_class(trigger_name: str):
    mapping = {
        "scheduled_trigger": ScheduledTrigger,
        "metric_based_trigger": MetricBasedTrigger,
        "none_trigger": NoneTrigger,
        "on_boarding_trigger": OnBoardingTrigger,
    }

    return mapping.get(trigger_name)


def map_resources_name_to_class(resource_name: str):
    mapping = {"cpu_resources": CpuResources, "gpu_resources": GpuResources}
    return mapping.get(resource_name)


def map_deployment_condition_name_to_class(deployment_condition_name: str):
    mapping = {"build_metric": BuildMetric}
    return mapping.get(deployment_condition_name)


def map_metric_name_to_class(metric_name: str):
    mapping = {"sql_metric": SqlMetric}
    return mapping.get(metric_name)


def map_auto_scaling_metric_type_proto_to_name(metric_type):
    mapping = {
        METRIC_TYPE_CPU: "cpu",
        METRIC_TYPE_LATENCY: "latency",
        METRIC_TYPE_MEMORY: "memory",
    }
    return mapping.get(metric_type)


def map_aggregation_type_proto_to_name(aggregation_type):
    mapping = {
        AGGREGATION_TYPE_AVERAGE: "avg",
        AGGREGATION_TYPE_MAX: "max",
        AGGREGATION_TYPE_MIN: "min",
        AGGREGATION_TYPE_SUM: "sum",
    }
    return mapping.get(aggregation_type)
