"""
A module acting as model_hub (Base Interface for further Clustering Models)
"""

from abc import ABC, abstractmethod


import numpy as np
import numpy.typing as npt


vector = npt.NDArray[np.float64]
predictions = npt.NDArray[np.int64]
numerical_features = npt.NDArray[vector]


class BaseClustering(ABC):
    """An Interface providing required protocols for Clustering Algorithms"""

    @abstractmethod
    def fit(self, x: numerical_features, **kwargs):
        """Fit a KMeans model to the given data

        Parameters
        ----------
        x: numerical_features :
            dataset containing numerical features
        **kwargs :
            anything specific to the child class (Clustering Algorithm)

        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def predict(self, x: numerical_features) -> predictions:
        """Predict on new datasets

        Parameters
        ----------
        x: numerical_features :
            dataset containing numerical features

        Returns
        -------
        preds: array_like
            Return the clusters per datapoint
        """
        preds = self.predict(x)
        return preds

    def fit_predict(self, x: numerical_features) -> predictions:
        """

        Parameters
        ----------
        x: numerical_features :
            dataset containing numerical features

        Returns
        -------
        preds: array_like
            Return the clusters per datapoint
        """
        self.fit(x)
        preds = self.predict(x)
        return preds
