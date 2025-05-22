from abc import ABC, abstractmethod


class BaseApiServices(ABC):

    @abstractmethod
    def get(self, url, parms=None):
        pass
