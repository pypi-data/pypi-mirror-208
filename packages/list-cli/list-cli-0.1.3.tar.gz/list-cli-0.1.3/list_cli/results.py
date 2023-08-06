from abc import ABC


class BaseResult(ABC):
    def __init__(
        self,
        had_error,
        had_output
    ):
        self._had_error = had_error
        self._had_output = had_output

    @property
    def had_error(self):
        return self._had_error

    @property
    def had_output(self):
        return self._had_output


class ErrorResult(BaseResult):
    def __init__(self, had_output=False):
        super().__init__(had_error=True, had_output=had_output)


class Result(BaseResult):
    def __init__(
        self,
        had_error=False,
        had_output=False
    ):
        super().__init__(had_error, had_output)


class SuccessResult(BaseResult):
    def __init__(self, had_output=False):
        super().__init__(had_error=False, had_output=had_output)
