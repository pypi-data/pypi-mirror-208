"""
A module for fitting/evaluating KMeans to Processed Datasets
"""

from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from yeroyan_clustering.modeling.base_models import BaseClustering


class SuperKmeans(BaseClustering):
    """Class performing KMeans related operations (Fitting, Elbow method, plots)

    ...

    Attributes
    ----------
    K : range
        Values of k used in Elbow-Method
    """
    def __init__(self, assumed_k: Optional[int] = None):
        self.K = range(2, 11)
        if assumed_k is not None:
            self.model = KMeans(n_clusters=assumed_k)

    def fit(self, x: pd.DataFrame | np.ndarray, k: Optional[int] = 3):
        """Fit a KMeans model to the given data

        Parameters
        ----------
        x: pd.DataFrame | np.ndarray :
            Processed (numerical features) dataframe subject to clustering
        k: Optional[int] :
            number of clusters
            (Default value = 3)

        Returns
        -------
        None
        """

        if k is not None:
            self.model = KMeans(k)

        if isinstance(x, pd.DataFrame):
            x = x.values

        self.model.fit(x)

    def predict(self, x: pd.DataFrame) -> np.ndarray[np.int64]:
        """Predict on new datasets

        Parameters
        ----------
        x: pd.DataFrame | np.ndarray :
            Processed (numerical features) dataframe subject to clustering


        Returns
        -------
        predictions: np.ndarray[np.int64]
            Array of integers specifying the predicted clusters
        """
        predictions = self.model.predict(x)
        return predictions

    def choose_k(self, x: pd.DataFrame):
        """Perform Elbow Method

        Iterate of self.K range of k-values
        Fit KMeans with all those k-values
        Calculate and store the inertia and silhouette scores
        Plot both of them to choose best K according to the Elbow Method

        Parameters
        ----------
        x: pd.DataFrame | np.ndarray :
            Processed (numerical features) dataframe subject to clustering

        Returns
        -------
        None
        """
        ssd = []
        silhouette_scores = []

        for k in self.K:
            kmeans = KMeans(n_clusters=k, max_iter=300, random_state=None)
            kmeans = kmeans.fit(x)
            label = kmeans.labels_
            ssd.append(kmeans.inertia_)
            sil_coeff = silhouette_score(x, label, metric='euclidean')
            silhouette_scores.append(sil_coeff)

        plt.grid()
        plt.tight_layout()
        plt.subplot(121)
        plt.plot(self.K, ssd, marker='o')
        plt.xlabel('k')
        plt.ylabel('Sum_of_squared_distances')
        plt.title('Elbow Method (Intertia) For Optimal k')
        # plt.show()

        plt.subplot(122)
        plt.plot(self.K, silhouette_scores, marker='*')
        plt.xlabel('k')
        plt.ylabel('Silthoute Score')
        plt.title('Elbow Method (Silhouette Score) For Optimal k')
        # plt.show()
