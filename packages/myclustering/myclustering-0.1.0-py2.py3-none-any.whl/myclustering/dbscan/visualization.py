"""
This module provides functions for visualizing clustering results.

Functions:
- plot_dbscan_pca(X, epsilon, min_points): Performs DBSCAN clustering on the given data and visualizes the resulting
clusters in 2D space using PCA. Outliers are marked as red crosses.
"""

from myclustering.kmeans.kmeans import euclidean_distance
from myclustering.dbscan.dbscan import DBSCAN
from myclustering.pca.pca import PCA
import matplotlib.pyplot as plt


def plot_dbscan_pca(X, epsilon, min_points):
    """
    Performs DBSCAN clustering on the given data and visualizes the resulting clusters in 2D space using PCA.
    Outliers are marked as red crosses.

    Parameters:
    - X (numpy.ndarray): The data to be clustered.
    - epsilon (float): The maximum distance between two points for them to be considered as in the same neighborhood.
    - min_points (int): The minimum number of points required to form a dense region.

    Returns:
    None.
    """
    # Initialize DBSCAN algorithm
    dbscan = DBSCAN(epsilon=epsilon, min_points=min_points, diss_func=euclidean_distance)

    # Initialize PCA algorithm with 2 principal components
    pca = PCA(n_components=2)
    # Transform the data into 2 principal components
    pca.fit(X)
    X_pca = pca.transform(X)
    # Get the cluster labels assigned by DBSCAN
    dbscan.fit(X)
    labels = dbscan.labels
    # Visualize the clusters in 2D space
    plt.scatter(X_pca[labels != -1, 0], X_pca[labels != -1, 1], c=labels[labels != -1], cmap='viridis')
    plt.scatter(X_pca[labels == -1, 0], X_pca[labels == -1, 1], c='red', marker='x', label='outliers')
    plt.legend()
    plt.title("DBSCAN clustering with PCA visualization")
    plt.show()
