import tensorflow as tf
import numpy as np
from abstractions.analyzing_model import AnalyzingModel
from sklearn.preprocessing import MinMaxScaler


class CNNModel(AnalyzingModel):
    def __init__(self, window_size=30, features=1):
        self.window_size = window_size
        self.features = features
        self.model = self._build_model()
        self.scaler = MinMaxScaler()

    def _build_model(self):
        model = tf.keras.Sequential(
            [
                tf.keras.layers.Conv1D(
                    filters=64,
                    kernel_size=3,
                    activation="relu",
                    input_shape=(self.window_size, self.features),
                ),
                tf.keras.layers.MaxPooling1D(pool_size=2),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(64, activation="relu"),
                tf.keras.layers.Dense(1),
            ]
        )
        model.compile(optimizer="adam", loss="mse")
        return model

    def _preprocess(self, data):
        sequences = []
        for i in range(len(data) - self.window_size):
            sequences.append(data[i : i + self.window_size])
        return np.array(sequences)

    def train(self, data):
        scaled_data = self.scaler.fit_transform(data)
        X = self._preprocess(scaled_data)
        y = scaled_data[self.window_size :]
        self.model.fit(X, y, epochs=10, batch_size=32, verbose=0)
        return {"status": "success", "message": "Model trained successfully"}

    def predict(self, data, horizon=5):
        scaled_data = self.scaler.transform(data)
        X = self._preprocess(scaled_data)
        predictions = []

        current_sequence = X[-1]
        for _ in range(horizon):
            next_pred = self.model.predict(np.expand_dims(current_sequence, axis=0))
            predictions.append(next_pred[0, 0])
            current_sequence = np.vstack([current_sequence[1:], next_pred])

        predictions = np.array(predictions).reshape(-1, 1)
        return self.scaler.inverse_transform(predictions)

    def analyze(self, data):
        scaled_data = self.scaler.transform(data)
        X = self._preprocess(scaled_data)
        predictions = self.model.predict(X)

        mse = np.mean((predictions - scaled_data[self.window_size :]) ** 2)
        trend = "up" if predictions[-1] > predictions[-2] else "down"

        return {
            "mse": float(mse),
            "trend": trend,
            "last_value": float(
                self.scaler.inverse_transform(predictions[-1].reshape(1, -1))[0, 0]
            ),
        }
