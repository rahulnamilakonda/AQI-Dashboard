from abc import ABC, abstractmethod


class BaseApiServices(ABC):

    @abstractmethod
    def get(url):
        pass
