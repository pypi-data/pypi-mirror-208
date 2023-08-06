from dependency_injector import containers, providers
from qwak.inner.tool.grpc.grpc_tools import create_grpc_channel


class QwakContainer(containers.DeclarativeContainer):
    """
    Qwak CLI dependencies
    """

    config = providers.Configuration(strict=True)

    core_grpc_channel = providers.Singleton(
        create_grpc_channel,
        url=config.grpc.core.address,
        enable_ssl=config.grpc.core.enable_ssl,
    )

    unauthenticated_core_grpc_channel = providers.Singleton(
        create_grpc_channel,
        url=config.grpc.core.address,
        enable_ssl=True,
        enable_auth=False,
    )
