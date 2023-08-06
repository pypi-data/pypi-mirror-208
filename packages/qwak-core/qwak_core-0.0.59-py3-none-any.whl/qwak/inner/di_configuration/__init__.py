import os

from .account import UserAccountConfiguration
from .containers import QwakContainer


def wire_dependencies():
    container = QwakContainer()

    default_config_file = os.path.join(os.path.dirname(__file__), "config.yml")
    container.config.from_yaml(default_config_file)

    from qwak.clients import (
        administration,
        alert_management,
        analytics,
        audience,
        automation_management,
        autoscaling,
        batch_job_management,
        build_management,
        build_orchestrator,
        data_versioning,
        deployment,
        feature_store,
        file_versioning,
        kube_deployment_captain,
        logging_client,
        model_management,
        project,
        user_application_instance,
    )

    container.wire(
        packages=[
            administration,
            alert_management,
            audience,
            automation_management,
            autoscaling,
            analytics,
            batch_job_management,
            build_management,
            build_orchestrator,
            data_versioning,
            deployment,
            file_versioning,
            kube_deployment_captain,
            logging_client,
            model_management,
            project,
            feature_store,
            user_application_instance,
        ]
    )

    return container
