"""
A module for performing dimensionality reduction and the corresponding plots
"""

import time
from typing import Optional

import numpy as np
import pandas as pd
import seaborn as sns
from loguru import logger
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE


class SuperTSNE:
    def __init__(self):
        """Init two t-SNE instances (for 2d & 3d visualisations)"""
        self.model_2d = TSNE(n_components=2, verbose=0, perplexity=30, n_iter=300)
        self.model_3d = TSNE(n_components=3, verbose=0, perplexity=50, n_iter=300)

    def transform(self, x: pd.DataFrame | np.ndarray, dim: int = 2) -> np.ndarray:
        """Fit one of the t-SNE models and then predict with it (transform)

        Parameters
        ----------
        x: pd.DataFrame | np.ndarray :
            The High Dimensional Dataset (with numeric features)
        dim: int :
            The numer of dimensions to project into {2, 3}
            (Default value = 2)

        Returns
        -------
        tsne_results: array_like
            the t-SNE embedings
            shape -> (number of samples, dim)
        """
        time_start = time.time()
        try:
            if dim == 2:
                tsne_results = self.model_2d.fit_transform(x)
            else:
                tsne_results = self.model_3d.fit_transform(x)
        except ValueError as v:
            logger.error(v.__str__())
            self.model_2d = TSNE(n_components=2, verbose=0, perplexity=5, n_iter=300)
            self.model_3d = TSNE(n_components=3, verbose=0, perplexity=5, n_iter=300)
            if dim == 2:
                tsne_results = self.model_2d.fit_transform(x)
            else:
                tsne_results = self.model_3d.fit_transform(x)
        print('t-SNE done! Time elapsed: {} seconds'.format(time.time() - time_start))
        return tsne_results

    def visualise(self, x: pd.DataFrame | np.ndarray, y: Optional[np.ndarray] = None, dim: int = 2):
        """

        Parameters
        ----------
        x: pd.DataFrame | np.ndarray :
            The High Dimensional Dataset to be visualised in lower dimensions
        y: Optional[np.ndarray] :
            A categorical (by semantics/nature) feature to color the plot (e.g. male vs female)
            (Default value = None) - all the points are colored same
        dim: int :
            The numer of dimensions to project into {2, 3}
            (Default value = 2)

        Returns
        -------
        None
        """
        embeddings = self.transform(x, dim)
        n = len(embeddings)
        t1 = embeddings[:, 0].reshape([n, 1])
        t2 = embeddings[:, 1].reshape([n, 1])
        t3 = embeddings[:, -1].reshape([n, 1])
        if dim == 2:
            embeddings = np.concatenate([t1, t2], axis=1)
        else:
            embeddings = np.concatenate([t1, t2, t3], axis=1)
        columns = [f'Dim_{i}' for i in range(dim)] + ['y']
        if y is None:
            y = np.zeros((n, 1), dtype=np.int64)
        else:
            y = y.reshape([n, 1])
        df = pd.DataFrame(np.concatenate([embeddings, y], axis=1), columns=columns)

        if dim == 2:
            plt.figure(figsize=(14,5))
            sns.scatterplot(
                x=columns[0], y=columns[1],
                hue="y",
                palette=sns.color_palette("hls", 10),
                data=df,
                legend="full",
                alpha=0.3
            )
            plt.show()
        else:
            np.random.seed(42)
            rndperm = np.random.permutation(df.shape[0])
            ax = plt.figure(figsize=(14, 5)).add_subplot(projection='3d')
            ax.scatter(
                xs=df.loc[rndperm, :][columns[0]],
                ys=df.loc[rndperm, :][columns[1]],
                zs=df.loc[rndperm, :][columns[2]],
                c=df.loc[rndperm, :]["y"],
                cmap='tab10'
            )
            ax.set_xlabel('tsne-one')
            ax.set_ylabel('tsne-two')
            ax.set_zlabel('tsne-three')
            plt.show()




