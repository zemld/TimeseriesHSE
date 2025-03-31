from abc import ABC, abstractmethod
import joblib
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf


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

    def save(self, path):
        model_type = self.__class__.__name__.replace("Model", "").lower()
        self.model.save(f"{path}/{model_type}_model.keras")
        joblib.dump(self.scaler, f"{path}/scaler.joblib")
        return {"status": "success", "path": path}

    def load(self, path):
        model_type = self.__class__.__name__.replace("Model", "").lower()
        self.model = tf.keras.models.load_model(f"{path}/{model_type}_model.keras")
        try:
            self.scaler = joblib.load(f"{path}/scaler.joblib")
        except (FileNotFoundError, ValueError):
            self.scaler = MinMaxScaler()
        return {"status": "success", "path": path}
