"""
This module contains functions for visualizing K-means clustering using PCA.

Functions:
----------
plot_kmeans_pca(X, n_clusters):
    Visualize K-means clustering in 2D space using PCA.

"""

import matplotlib.pyplot as plt
from myclustering.kmeans.kmeans import KMeans
from myclustering.pca.pca import PCA


def plot_kmeans_pca(X, n_clusters):

    """
    Plots a 2D scatter plot of the input data after applying KMeans clustering and PCA.

    Parameters:
    -----------
    X : numpy.ndarray
        Input data, where each row corresponds to a sample and each column corresponds to a feature.
    n_clusters : int
        The number of clusters to use in the KMeans algorithm.

    Returns:
    --------
    None
    """

    # Initialize KMeans algorithm with the specified number of clusters
    kmeans = KMeans(K=n_clusters, max_iters=100, plot_steps=False)

    # Initialize PCA algorithm with 2 principal components
    pca = PCA(n_components=2)

    # Transform the data into 2 principal components
    pca.fit(X)
    X_pca = pca.transform(X)

    # Fit KMeans to the input data and get the cluster labels
    labels = kmeans.fit(X)

    # Visualize the clusters in 2D space
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='viridis')
    plt.title("K-means clustering with PCA visualization")
    plt.show()
