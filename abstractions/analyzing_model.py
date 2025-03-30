from abc import ABC, abstractmethod


class AnalyzingModel(ABC):
    @abstractmethod
    def train(self, data):
        pass

    @abstractmethod
    def predict(self, data, horizon=5):
        pass

    @abstractmethod
    def analyze(self, data):
        pass

    @abstractmethod
    def save(self, path):
        pass

    @abstractmethod
    def load(self, path):
        pass
