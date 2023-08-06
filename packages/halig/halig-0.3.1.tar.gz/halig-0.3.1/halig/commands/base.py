from abc import ABC, abstractmethod

from halig.settings import Settings


class ICommand(ABC):
    @abstractmethod
    def run(self):
        ...  # pragma: no cover


class BaseCommand(ICommand):
    def __init__(self, settings: Settings, *args, **kwargs):
        self.settings = settings
