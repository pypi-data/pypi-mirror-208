from dependency_injector import containers, providers
from qwak.model.decorators.api_implementation import create_decorator_function


class QwakRuntimeContainer(containers.DeclarativeContainer):
    """
    Qwak Core's Runtime Dependency Injection Container
    """

    api_decorator_function_creator = providers.Object(create_decorator_function)
