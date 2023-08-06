from typing import Union

from qwak.model.base import QwakModel

from .adapters.input import get_input_adapter
from .adapters.output import get_output_adapter


def run_local(model: QwakModel, payload: Union[str, bytes]):
    """
    Invokes the .build, .initalize_model, and in order and then invokes the input adapter, calls the predict method
    and invokes the output adapter.
    :param model: the model to run locally
    :param payload: a string or bytes with the input data
    :return: a string or bytes with the model output
    """
    if not (hasattr(model, "initialized") and model.initialized):
        model.build()
        model.initialize_model()
        setattr(model, "initialized", True)
    input_adapter = get_input_adapter(model)
    output_adapter = get_output_adapter(model)
    input_data = input_adapter.extract_user_func_args(payload)
    output_data = model.predict(input_data)
    return output_adapter.pack_user_func_return_value(output_data)
