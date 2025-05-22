class AppExceptions(Exception):
    def __init__(self, error, prefix):
        self.error = error
        self.prefix = prefix

    def __str__(self):
        return f"{self.prefix}: {self.error}"


class TimeOutException(AppExceptions):
    def __init__(self, error):
        super().__init__(
            error,
            "TimeOutException",
        )


class ConnectionException(AppExceptions):
    def __init__(
        self,
        error,
    ):
        super().__init__(error, "ConnectionException")


class ClientSideException(AppExceptions):
    def __init__(
        self,
        error,
    ):
        super().__init__(error, "ClientSideExceptions")


class ServerSideException(AppExceptions):
    def __init__(self, error):
        super().__init__(error, "ServerSideException")


class FetchDataException(AppExceptions):
    def __init__(self, error):
        super().__init__(error, "FetchDataException")


class WAQIErrorException(AppExceptions):
    def __init__(self, error):
        super().__init__(error, "WAQIErrorException")
