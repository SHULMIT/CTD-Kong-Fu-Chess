from abc import ABC, abstractmethod


class BoardFormat(ABC):

    @abstractmethod
    def parse(self, text):
        pass

    @abstractmethod
    def serialize(self, board):
        pass