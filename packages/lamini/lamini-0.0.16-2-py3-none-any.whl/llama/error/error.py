class LlamaError(Exception):
    def __init__(
        self,
        message=None,
    ):
        super(LlamaError, self).__init__(message)


class APIError(LlamaError):
    pass


class AuthenticationError(LlamaError):
    pass


class RateLimitError(LlamaError):
    pass
