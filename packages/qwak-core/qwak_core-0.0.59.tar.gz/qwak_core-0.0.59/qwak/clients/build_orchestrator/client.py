import json
import re
from typing import Dict, List, Optional

import grpc
import yaml
from _qwak_proto.qwak.build.v1.build_api_pb2 import (
    GetBuildRequest,
    GetBuildResponse,
    ListBuildsRequest,
    ListBuildsResponse,
    LogPhaseStatusRequest,
    PhaseStatus,
    RegisterBuildRequest,
    RegisterBuildResponse,
    RegisterExperimentTrackingRequest,
    RegisterExperimentTrackingResponse,
    RegisterModelSchemaRequest,
    RegisterModelSchemaResponse,
    RegisterTagsRequest,
    RegisterTagsResponse,
    UpdateBuildStatusRequest,
    UpdateBuildStatusResponse,
)
from _qwak_proto.qwak.build.v1.build_api_pb2_grpc import BuildAPIStub
from _qwak_proto.qwak.build.v1.build_pb2 import BuildFilter, BuildStatus, ModelSchema
from _qwak_proto.qwak.builds.build_pb2 import (
    BuildEnv,
    BuildProperties,
    BuildPropertiesV1,
    CpuResources,
    DataTableDefinition,
    DockerEnv,
    GpuResources,
    MemoryUnit,
    ModelUriSpec,
    PythonEnv,
    RemoteBuildSpec,
)
from _qwak_proto.qwak.builds.build_url_pb2 import BuildVersioningUrlParams
from _qwak_proto.qwak.builds.builds_orchestrator_service_pb2 import (
    BuildModelRequest,
    CancelBuildModelRequest,
    CreateDataTableRequest,
    CreateDataTableResponse,
    GetBuildVersioningDownloadURLRequest,
    GetBuildVersioningDownloadURLResponse,
    GetBuildVersioningUploadURLRequest,
    GetBuildVersioningUploadURLResponse,
)
from _qwak_proto.qwak.builds.builds_orchestrator_service_pb2_grpc import (
    BuildsOrchestratorServiceStub,
)
from dependency_injector.wiring import Provide
from qwak.exceptions import QwakException
from qwak.inner.di_configuration import QwakContainer
from qwak.inner.tool.grpc.grpc_try_wrapping import grpc_try_catch_wrapper
from yaml import Loader


class BuildOrchestratorClient:
    def __init__(self, grpc_channel=Provide[QwakContainer.core_grpc_channel]):
        self._builds_orchestrator_stub_build_api = BuildAPIStub(grpc_channel)
        self._builds_orchestrator_stub = BuildsOrchestratorServiceStub(grpc_channel)

    @grpc_try_catch_wrapper("Failed to register build")
    def register_build(
        self,
        build_id: str,
        commit_id: str,
        model_id: str,
        build_config: str,
        tags: List[str] = None,
        steps: List[str] = None,
    ) -> RegisterBuildResponse:
        request = RegisterBuildRequest(
            buildId=build_id,
            commitId=commit_id,
            modelId=model_id,
            buildConfig=build_config,
            tags=tags,
            steps=steps,
        )
        return self._builds_orchestrator_stub_build_api.RegisterBuild(request)

    @grpc_try_catch_wrapper("Failed to update build status")
    def update_build_status(
        self, build_id: str, build_status: BuildStatus
    ) -> UpdateBuildStatusResponse:
        request = UpdateBuildStatusRequest(buildId=build_id, build_status=build_status)
        return self._builds_orchestrator_stub_build_api.UpdateBuildStatus(request)

    @grpc_try_catch_wrapper("Failed to register model schema")
    def register_model_schema(
        self, build_id: str, model_schema: ModelSchema
    ) -> RegisterModelSchemaResponse:
        request = RegisterModelSchemaRequest(
            build_id=build_id, model_schema=model_schema
        )
        return self._builds_orchestrator_stub_build_api.RegisterModelSchema(request)

    @grpc_try_catch_wrapper("Failed to register experiment tracking values")
    def register_experiment_tracking(
        self,
        build_id: str,
        params: Dict[str, str] = None,
        metrics: Dict[str, float] = None,
    ) -> RegisterExperimentTrackingResponse:
        request = RegisterExperimentTrackingRequest(
            build_id=build_id, params=params, metrics=metrics
        )
        return self._builds_orchestrator_stub_build_api.RegisterExperimentTracking(
            request
        )

    @grpc_try_catch_wrapper("Failed to register tags")
    def register_tags(
        self,
        build_id: str,
        tags: List[str],
    ) -> RegisterTagsResponse:
        request = RegisterTagsRequest(build_id=build_id, tags=tags)
        return self._builds_orchestrator_stub_build_api.RegisterTags(request)

    @grpc_try_catch_wrapper("Failed to list builds")
    def list_builds(
        self, model_uuid: str = "", build_filter: BuildFilter = None, **kwargs
    ) -> ListBuildsResponse:
        _model_uuid = model_uuid if model_uuid else kwargs.get("branch_id")
        if not _model_uuid:
            raise QwakException("missing argument model uuid or branch id.")

        request = ListBuildsRequest(model_uuid=_model_uuid, filter=build_filter)
        return self._builds_orchestrator_stub_build_api.ListBuilds(request)

    @grpc_try_catch_wrapper("Failed to get build")
    def get_build(self, build_id: str) -> GetBuildResponse:
        request = GetBuildRequest(build_id=build_id)
        return self._builds_orchestrator_stub_build_api.GetBuild(request)

    def is_build_exists(self, build_id: str) -> bool:
        try:
            build: GetBuildResponse = self.get_build(build_id)
            if build.build.build_spec.build_id == build_id:
                return True
            return False
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return False
            raise QwakException(
                f"Failed to check if build {build_id} is exists, error is {e.details()}"
            )

    @grpc_try_catch_wrapper("Failed to get build versioning upload url")
    def get_build_versioning_upload_url(
        self, build_id: str, model_id: str, tag: str
    ) -> GetBuildVersioningUploadURLResponse:
        """Get Upload pre signed url

        Args:
            model_id: Model ID
            build_id: Build ID
            tag: the tag to save the artifact by

        Returns:
            the pre signed upload url
        """
        return self._builds_orchestrator_stub.GetBuildVersioningUploadURL(
            GetBuildVersioningUploadURLRequest(
                params=BuildVersioningUrlParams(
                    build_id=build_id, model_id=model_id, tag=tag
                )
            )
        )

    @grpc_try_catch_wrapper("Failed to create download url")
    def get_build_versioning_download_url(
        self, build_id: str, model_id: str, tag: str
    ) -> GetBuildVersioningDownloadURLResponse:
        """Get Download pre signed url

        Args:
            model_id: Model ID
            build_id: Build ID
            tag: the tag to save the artifact by

        Returns:
            the pre signed download url
        """
        return self._builds_orchestrator_stub.GetBuildVersioningDownloadURL(
            GetBuildVersioningDownloadURLRequest(
                params=BuildVersioningUrlParams(
                    build_id=build_id, model_id=model_id, tag=tag
                )
            )
        )

    @grpc_try_catch_wrapper("Failed to define a table for the data")
    def define_build_data_table(
        self, build_id: str, model_id: str, tag: str, table: DataTableDefinition
    ) -> CreateDataTableResponse:
        """Define Build Data Table

        Args:
            model_id: Model ID
            build_id: Build ID
            tag: tag for the data
            table: the data to save the table for

        Returns:
            the pre signed download url
        """
        return self._builds_orchestrator_stub.CreateDataTable(
            CreateDataTableRequest(
                build_id=build_id,
                model_id=model_id,
                tag=tag,
                table=table,
            )
        )

    @grpc_try_catch_wrapper("Failed to log build phase status")
    def log_phase_status(
        self,
        build_id: str,
        phase_id: str,
        phase_status: PhaseStatus,
        duration_in_seconds: int,
    ) -> None:
        if build_id:
            request = LogPhaseStatusRequest(
                build_id=build_id,
                phase_id=phase_id,
                status=phase_status,
                phase_duration_in_seconds=duration_in_seconds,
            )
            self._builds_orchestrator_stub_build_api.LogPhaseStatus(request)

        else:
            print(f"No build id. Cannot log phase status: {phase_id} {phase_status}")

    def build_model(
        self,
        build_conf,
        verbose: int = 3,
        git_commit_id: str = "",
        resolved_model_url: str = "",
        build_code_path: str = "",
        build_v1_flag: bool = False,
        build_config_url: str = "",
        qwak_sdk_wheel_url: str = "",
        qwak_sdk_version_url: str = "",
        build_steps: Optional[List[str]] = None,
        sdk_version: str = "",
    ):
        """Initiate remote build

        Args:
            verbose: log verbosity level
            git_commit_id: commit id
            resolved_model_url: the url of model
            build_conf: the build configuration
            build_code_path: The code  path saved by qwak
            build_v1_flag:
            build_config_url:
            qwak_sdk_wheel_url:
            qwak_sdk_version_url:
            build_steps: List of the steps the build is comprised from
            sdk_version: The sdk version to build the

        Raises:
            QwakException: In case of failing to connect the service
        """
        build_steps = build_steps if build_steps else []

        try:
            request = self.__get_build_model_request(
                build_conf,
                verbose,
                git_commit_id,
                resolved_model_url,
                build_code_path,
                build_v1_flag,
                build_config_url,
                qwak_sdk_wheel_url,
                qwak_sdk_version_url,
                build_steps,
                sdk_version,
            )
            self._builds_orchestrator_stub.BuildModel(request)
        except grpc.RpcError as e:
            message = (
                f"Failed to build model, status [{e.code()}] details [{e.details()}]"
            )
            raise QwakException(message)

        except Exception as e:
            message = f"Failed to build model, details [{e}]"
            raise QwakException(message)

    @staticmethod
    def __get_build_model_request(
        build_conf,
        verbose: int = 3,
        git_commit_id: str = "",
        resolved_model_url: str = "",
        build_code_path: str = "",
        build_v1_flag: bool = False,
        build_config_url: str = "",
        qwak_sdk_wheel_url: str = "",
        qwak_sdk_version_url: str = "",
        build_steps: Optional[List[str]] = None,
        sdk_version: str = "",
    ) -> BuildModelRequest:
        request = BuildModelRequest(
            build_spec=RemoteBuildSpec(
                build_properties=BuildProperties(
                    build_id=build_conf.build_properties.build_id,
                    model_id=build_conf.build_properties.model_id,
                    branch=build_conf.build_properties.branch,
                    tags=build_conf.build_properties.tags,
                    model_uri=ModelUriSpec(
                        uri=resolved_model_url
                        or build_conf.build_properties.model_uri.uri,
                        git_credentials=build_conf.build_properties.model_uri.git_credentials,
                        git_credentials_secret=build_conf.build_properties.model_uri.git_credentials_secret,
                        git_branch=build_conf.build_properties.model_uri.git_branch,
                        commit_id=git_commit_id,
                        main_dir=build_conf.build_properties.model_uri.main_dir,
                    ),
                ),
                build_env=BuildEnv(
                    docker_env=DockerEnv(
                        base_image=build_conf.build_env.docker.base_image,
                        assumed_iam_role_arn=build_conf.build_env.docker.assumed_iam_role_arn,
                        no_cache=not build_conf.build_env.docker.cache,
                        env_vars=build_conf.build_env.docker.env_vars,
                    ),
                    python_env=PythonEnv(
                        git_credentials=build_conf.build_properties.model_uri.git_credentials,
                        git_credentials_secret=build_conf.build_properties.model_uri.git_credentials_secret,
                        qwak_sdk_version=sdk_version,
                        qwak_sdk_extra_index=build_conf.build_env.python_env.qwak_sdk_extra_index_url,
                    ),
                ),
                verbose=verbose,
                build_code_path=build_code_path,
                build_config=json.dumps(
                    yaml.load(build_conf.to_yaml(), Loader=Loader)  # nosec B506
                ),
                build_properties_v1=BuildPropertiesV1(
                    build_config_url=build_config_url,
                    qwak_sdk_wheel_url=qwak_sdk_wheel_url,
                    qwak_sdk_version_url=qwak_sdk_version_url,
                ),
                build_v1_flag=build_v1_flag,
                build_steps=build_steps,
            )
        )

        if build_conf.build_env.remote.resources.gpu_type:
            request.build_spec.gpu_resources.CopyFrom(
                GpuResources(
                    gpu_type=build_conf.build_env.remote.resources.gpu_type,
                    gpu_amount=build_conf.build_env.remote.resources.gpu_amount,
                )
            )
        else:
            request.build_spec.cpu_resources.CopyFrom(
                CpuResources(
                    cpu=build_conf.build_env.remote.resources.cpus,
                    memory_amount=int(
                        re.sub(
                            r"\D",
                            "",
                            build_conf.build_env.remote.resources.memory,
                        )
                    ),
                    memory_units=map_memory_units(
                        build_conf.build_env.remote.resources.memory
                    ),
                )
            )

        return request

    def cancel_build_model(self, build_id: str):
        """cancel remote build process

        Args:
            build_id: The build Id to cancel

        Raises:
            QwakException: In case of failing to connect the service
        """
        try:
            self._builds_orchestrator_stub.CancelBuildModel(
                CancelBuildModelRequest(build_id=build_id)
            )
        except grpc.RpcError as e:
            raise QwakException(
                f"Failed to cancel build, status [{e.code()}] details [{e.details()}]"
            )


def map_memory_units(memory):
    memory_unit = re.sub(r"\d+", "", memory)
    if memory_unit == "Gi":
        return MemoryUnit.GIB
    elif memory_unit == "Mib":
        return MemoryUnit.MIB
    else:
        return MemoryUnit.UNKNOWN_MEMORY_UNIT
