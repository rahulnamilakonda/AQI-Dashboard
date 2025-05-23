from dataclasses import dataclass, InitVar, field


@dataclass
class OpenQIResponse:

    _response: any = field(default=None)

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, val):
        self._response = val

    def __str__(self):
        return f"Response: {self.response}"
