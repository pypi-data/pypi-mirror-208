"""
Module for performing the elbow method using the silhouette score for KMeans clustering.

Functions:
- elbow_method(X, max_clusters=10):
    Performs the elbow method using the silhouette score for KMeans clustering on the given dataset X.
    It computes the silhouette score for k in [2, max_clusters], where max_clusters is a positive integer.
    It then plots the silhouette scores against the number of clusters k and shows the plot.
    Returns: None
"""

import matplotlib.pyplot as plt
from myclustering.kmeans.kmeans import KMeans
from myclustering.kmeans.silhouette import silhouette_score


def elbow_method(X, max_clusters=10):
    """
    Performs the elbow method using the silhouette score for KMeans clustering on the given dataset X.

    Parameters:
    - X: a numpy array or matrix of shape (n_samples, n_features) representing the dataset.
    - max_clusters: an integer, the maximum number of clusters to try.

    Returns: None
    """
    sil_scores = []
    for i in range(2, max_clusters+1):
        kmeans = KMeans(K=i, max_iters=100, plot_steps=False)
        sil_scores.append(silhouette_score(X, kmeans))

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(range(2, max_clusters+1), sil_scores, 'bx-')
    ax.set_xlabel('k')
    ax.set_ylabel('Silhouette Score')
    ax.set_title('The Silhouette Score Elbow Method')
    plt.show()
