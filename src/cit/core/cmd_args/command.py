from abc import ABC, abstractmethod
from argparse import Namespace

from cit.core.repository import Repository

class Command(ABC):

    @abstractmethod
    def execute(self, repo: Repository, args: Namespace):
        pass