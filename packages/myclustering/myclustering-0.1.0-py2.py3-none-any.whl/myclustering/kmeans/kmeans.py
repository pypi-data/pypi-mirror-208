"""
This module contains the implementation of the KMeans algorithm, used for clustering data.

Classes:
    KMeans

Functions:
    euclidean_distance

"""

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)


def euclidean_distance(x1, x2):
    """
    Calculate the euclidean distance between two points.

    Args:
        x1 (numpy array): First point.
        x2 (numpy array): Second point.

    Returns:
        float: Euclidean distance between the two points.
    """
    return np.sqrt(np.sum((x1 - x2)**2))


class KMeans():
    """
    Class for KMeans clustering.

    Attributes:
        Attributes:
        K (int): The number of clusters, default = 5.
        max_iters (int): The maximum number of iterations for k-means.
        plot_steps (bool): Whether or not to plot the steps of k-means.


    Methods:
        fit(X): Fits the KMeans model to the input data.
        plot(): Plots the clusters and centroids.

    """

    def __init__(self, K=5, max_iters=100, plot_steps=False):
        """
        Initialize the KMeans object.

        Args:
            K (int, optional): Number of clusters. Default is 5.
            max_iters (int, optional): Maximum number of iterations. Default is 100.
            plot_steps (bool, optional): Whether to plot the data at each iteration. Default is False.
        """
        self.K = K
        self.max_iters = max_iters
        self.plot_steps = plot_steps

        # list of sample indices for each cluster
        self.clusters = [[] for _ in range(self.K)]
        # the centers (mean feature vector) for each cluster
        self.centroids = []

    def fit(self, X):
        """
        Fits the KMeans model to the input data.

        Args:
            X (numpy array): Input data.

        Returns:
            numpy array: Cluster labels for each sample.
        """
        self.X = X
        self.n_samples, self.n_features = X.shape

        # initialize
        random_sample_idxs = np.random.choice(self.n_samples, self.K, replace=False)
        self.centroids = [self.X[idx] for idx in random_sample_idxs]

        # Optimize clusters
        for _ in range(self.max_iters):
            # Assign samples to closest centroids (create clusters)
            self.clusters = self._create_clusters(self.centroids)

            if self.plot_steps:
                self.plot()

            # Calculate new centroids from the clusters
            centroids_old = self.centroids
            self.centroids = self._get_centroids(self.clusters)

            # check if clusters have changed
            if self._is_converged(centroids_old, self.centroids):
                break

            if self.plot_steps:
                self.plot()

        # Classify samples as the index of their clusters
        return self._get_cluster_labels(self.clusters)

    def _get_cluster_labels(self, clusters):
        """
        Returns the cluster labels for each sample.

        Args:
            clusters (list): List of clusters, where each cluster is a list of sample indices.

        Returns:
            numpy array: Cluster labels for each sample.
        """
        # each sample will get the label of the cluster it was assigned to
        labels = np.empty(self.n_samples)

        for cluster_idx, cluster in enumerate(clusters):
            for sample_index in cluster:
                labels[sample_index] = cluster_idx
        return labels

    def _create_clusters(self, centroids):
        """
        Assigns the samples to the closest centroids to create clusters.

        Parameters
        ----------
        centroids : array-like, shape (n_clusters, n_features)
            The centroid locations in feature space.

        Returns
        -------
        clusters : list of lists
            The indices of the samples belonging to each cluster.
        """
        clusters = [[] for _ in range(self.K)]
        for idx, sample in enumerate(self.X):
            centroid_idx = self._closest_centroid(sample, centroids)
            clusters[centroid_idx].append(idx)
        return clusters

    def _closest_centroid(self, sample, centroids):
        """
        Computes the index of the closest centroid for a given sample.

        Parameters
        ----------
        sample : array-like, shape (n_features,)
            The feature vector of a sample.

        centroids : array-like, shape (n_clusters, n_features)
            The centroid locations in feature space.

        Returns
        -------
        closest_index : int
            The index of the closest centroid for the given sample.
        """
        distances = [euclidean_distance(sample, point) for point in centroids]
        closest_index = np.argmin(distances)
        return closest_index

    def _get_centroids(self, clusters):
        """
        Computes the mean of the samples in each cluster and assigns it to the
        corresponding centroid.

        Parameters
        ----------
        clusters : list of lists
            The indices of the samples belonging to each cluster.

        Returns
        -------
        centroids : array-like, shape (n_clusters, n_features)
            The updated centroid locations in feature space.
        """
        centroids = np.zeros((self.K, self.n_features))
        for cluster_idx, cluster in enumerate(clusters):
            cluster_mean = np.mean(self.X[cluster], axis=0)
            centroids[cluster_idx] = cluster_mean
        return centroids

    def _is_converged(self, centroids_old, centroids):
        """
        Checks if the algorithm has converged, i.e. if the centroids have
        stopped moving.

        Parameters
        ----------
        centroids_old : array-like, shape (n_clusters, n_features)
            The centroid locations in feature space from the previous iteration.

        centroids : array-like, shape (n_clusters, n_features)
            The updated centroid locations in feature space.

        Returns
        -------
        is_converged : bool
            Whether the centroids have stopped moving or not.
        """
        distances = [euclidean_distance(centroids_old[i], centroids[i]) for i in range(self.K)]
        return sum(distances) == 0

    def plot(self):
        """
        Plots the clusters and centroids.

        Raises
        ------
        Exception
            If the data has more than 2 features.
        """
        if self.n_features > 2:
            raise Exception("Cannot plot data with more than 2 features")

        fig, ax = plt.subplots(figsize=(12, 8))

        for i, index in enumerate(self.clusters):
            point = self.X[index].T
            ax.scatter(*point)

        for point in self.centroids:
            ax.scatter(*point, marker="*", color='black', linewidth=5)

        plt.show()
