from typing import List

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from ..column_types import (AnyTypePredictor, ColumnTypePredictor,
                            ItalianFiscalCodeType, ItalianVATType)


class DataframeEmbedding:

    def __init__(self, use_multiprocessing: bool = True):
        """Create new DataframeEmbedding.

        Parameters
        -----------------------
        use_multiprocessing: bool = True,
            Wether to use multiprocessing.
        """
        self._predictor = AnyTypePredictor(use_multiprocessing)
        self._encoder = LabelEncoder().fit(
            self._predictor.supported_types + ["Error"]
        )
        self._italian_vat_codes = ItalianVATType()
        self._fiscal_codes = ItalianFiscalCodeType()

    def get_column(self, df: pd.DataFrame, validator: ColumnTypePredictor) -> List:
        for column in df.columns:
            predictions = validator.validate(df[column])
            if any(predictions):
                return [
                    value if prediction else None
                    for value, prediction in zip(df[column], predictions)
                ]
        return (None,)*df.shape[0]

    def get_fiscal_codes(self, df: pd.DataFrame) -> List[str]:
        return self.get_column(df, self._fiscal_codes)

    def get_italian_vat_codes(self, df: pd.DataFrame) -> List[str]:
        return self.get_column(df, self._italian_vat_codes)

    def transform(self, df: pd.DataFrame, y: np.ndarray = None) -> np.ndarray:
        """Encode given dataframe into a vector space."""
        fiscal_codes = self.get_fiscal_codes(df)
        italian_vat_codes = self.get_italian_vat_codes(df)

        predictors_number = len(self._predictor.supported_types)
        predictions = np.zeros((
            df.shape[0],
            predictors_number
        ))
        X = np.zeros((
            df.shape[0]*df.shape[1],
            (predictors_number)*2
        ))

        for i, column in enumerate(df.columns):
            predictions[:, :predictors_number] = np.array(self._predictor.predict_values(
                df[column],
                fiscal_codes=fiscal_codes,
                italian_vat_codes=italian_vat_codes
            )).T

            vertical_cut = slice(i*df.shape[0], (i+1)*df.shape[0])
            X[vertical_cut, :predictions.shape[1]
              ] = predictions  # pylint: disable=unsubscriptable-object

            indices = list(range(
                predictions.shape[1], predictions.shape[1]*2))  # pylint: disable=unsubscriptable-object
            X[vertical_cut, indices] = predictions.mean(axis=0)

        if y is not None:
            return X, self._encoder.transform(y.T.values.ravel())
        return X

    def reverse_label_embedding(self, encoded_labels: np.ndarray, df: pd.DataFrame) -> np.ndarray:
        decoded_labels = self._encoder.inverse_transform(encoded_labels)

        decoded_labels = decoded_labels.reshape((df.shape[1], df.shape[0]))

        return pd.DataFrame(
            decoded_labels.T,
            columns=df.columns,
            index=df.index
        )
