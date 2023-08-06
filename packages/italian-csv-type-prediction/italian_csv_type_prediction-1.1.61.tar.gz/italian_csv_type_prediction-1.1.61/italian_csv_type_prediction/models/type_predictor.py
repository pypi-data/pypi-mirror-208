import os

import compress_pickle
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from ..embedding import DataframeEmbedding
from ..utils import logger


class TypePredictor:

    def __init__(self, local_path: str = "type_predictor.pkl.gz"):

        self._embedder = DataframeEmbedding()
        self._local_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            local_path
        )
        self._model = self._load_model()

    def fit(self, X: np.array, y: np.array):
        self._model = DecisionTreeClassifier(
            max_depth=50,
            random_state=42,
            class_weight="balanced",
            min_samples_split=50
        ).fit(X, y)
        self._save_model()

    def _save_model(self):
        compress_pickle.dump(self._model, self._local_path)

    def _load_model(self):
        if os.path.exists(self._local_path):
            return compress_pickle.load(self._local_path)
        return None

    def predict_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return dataframe with given dataframe type predictions."""
        logger.info("Transforming given DataFrame to embedding.")
        transformed_dataframe = self._embedder.transform(df)
        logger.info("Executing predictions on given DataFrame.")
        predictions = self._model.predict(transformed_dataframe)
        logger.info(
            "Executing reverse transformation of the predictions from embedding.")
        return self._embedder.reverse_label_embedding(
            predictions,
            df
        )
