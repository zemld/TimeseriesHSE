import tensorflow as tf
import numpy as np
from abstractions.analyzing_model import AnalyzingModel
from sklearn.preprocessing import MinMaxScaler


class TFTModel(AnalyzingModel):
    def __init__(self, window_size=30, features=1, num_heads=4):
        self.window_size = window_size
        self.features = features
        self.num_heads = num_heads
        self.model = self._build_model()
        self.scaler = MinMaxScaler()

    def _build_model(self):
        inputs = tf.keras.layers.Input(shape=(self.window_size, self.features))
        x = tf.keras.layers.LayerNormalization()(inputs)
        positional_encoding = self._positional_encoding(self.window_size, 64)
        x = tf.keras.layers.Dense(64)(x)
        x = x + positional_encoding

        attention_output = tf.keras.layers.MultiHeadAttention(
            num_heads=self.num_heads, key_dim=16
        )(x, x)
        x = tf.keras.layers.Add()([x, attention_output])
        x = tf.keras.layers.LayerNormalization()(x)

        ffn_output = self._feed_forward_network(x)
        x = tf.keras.layers.Add()([x, ffn_output])
        x = tf.keras.layers.LayerNormalization()(x)

        x = tf.keras.layers.GlobalAveragePooling1D()(x)
        outputs = tf.keras.layers.Dense(1)(x)

        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer="adam", loss="mse")

        return model

    def _positional_encoding(self, length, depth):
        positions = np.arange(length)[:, np.newaxis]
        depths = np.arange(depth)[np.newaxis, :] / depth
        angle_rates = 1 / (10000**depths)
        angle_rads = positions * angle_rates

        pos_encoding = np.zeros((1, length, depth))
        pos_encoding[0, :, 0::2] = np.sin(angle_rads[:, 0::2])
        pos_encoding[0, :, 1::2] = np.cos(angle_rads[:, 1::2])

        return tf.cast(pos_encoding, dtype=tf.float32)

    def _feed_forward_network(self, x):
        ffn = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(128, activation="relu"),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(64),
            ]
        )
        return ffn(x)

    def _preprocess(self, data):
        sequences = []
        for i in range(len(data) - self.window_size):
            sequences.append(data[i : i + self.window_size])
        return np.array(sequences)

    def train(self, data):
        scaled_data = self.scaler.fit_transform(data)
        X = self._preprocess(scaled_data)
        y = scaled_data[self.window_size :]

        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="loss", patience=5, restore_best_weights=True
        )

        self.model.fit(
            X, y, epochs=20, batch_size=32, callbacks=[early_stopping], verbose=0
        )
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
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions - scaled_data[self.window_size :]))

        if len(predictions) >= 2:
            trend = "up" if predictions[-1] > predictions[-2] else "down"
        else:
            trend = "unknown"

        return {
            "mse": float(mse),
            "rmse": float(rmse),
            "mae": float(mae),
            "trend": trend,
            "last_value": float(
                self.scaler.inverse_transform(predictions[-1].reshape(1, -1))[0, 0]
            ),
        }
