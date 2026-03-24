from abc import ABC, abstractmethod
from argparse import Namespace

class Command(ABC):

    @abstractmethod
    def execute(self, repo, args: Namespace):
        pass