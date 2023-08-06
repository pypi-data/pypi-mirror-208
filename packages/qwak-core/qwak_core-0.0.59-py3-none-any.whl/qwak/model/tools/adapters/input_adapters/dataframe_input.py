import json

import pandas
from qwak.exceptions import QwakHTTPException

from .string_input import StringInput


class DataframeInput(StringInput):
    def __init__(
        self,
        **base_kwargs,
    ):
        super().__init__(**base_kwargs)

        # Verify pandas imported properly and retry import if it has failed initially
        try:
            import pandas  # noqa: F401
        except ImportError:
            raise ImportError("Pandas package is required to use DataframeInput.")

    def extract_user_func_args(self, data: str) -> "pandas.DataFrame":
        try:
            return pandas.DataFrame.from_dict(json.loads(data), orient="columns")
        except Exception as e:
            raise QwakHTTPException(
                status_code=400,
                message=f"Error loading DataFrame input: {e}.",
            )
