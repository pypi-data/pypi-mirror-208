"""
DBSCAN clustering algorithm.

DBSCAN (Density-Based Spatial Clustering of Applications with Noise) is a popular clustering algorithm that groups
together points that are closely packed together while marking points that lie alone in low-density regions as
noise.

This implementation of DBSCAN takes three parameters: epsilon, min_points, and diss_func. Epsilon is the maximum
distance/dissimilarity between two points to be considered as in the neighborhood of each other. Min_points is the
minimum number of points in a neighborhood for a point to be considered as a core point (a member of a cluster). This
includes the point itself. Diss_func is the dissimilarity measure to compute the dissimilarity/distance between two
data points.

Usage:
    >>> from myclustering.dbscan import DBSCAN
    >>> dbscan = DBSCAN(epsilon=0.5, min_points=5)
    >>> clusters = dbscan.fit(X)

"""

import numpy as np
from myclustering.kmeans.kmeans import euclidean_distance


class DBSCAN:
    """
    Implementation of DBSCAN clustering algorithm.

    Parameters
    ----------
    diss_func : function, optional, default: euclidean_distance
        Dissimilarity function used to calculate the distance between two data points.
    epsilon : float, optional, default: 0.5
        The radius within which the algorithm searches for neighbors.
    min_points : int, optional, default: 5
        The minimum number of neighbors required to form a cluster.

    Attributes
    ----------
    eps : float
        The radius within which the algorithm searches for neighbors.
    min_points : int
        The minimum number of neighbors required to form a cluster.
    diss_func : function
        Dissimilarity function used to calculate the distance between two data points.
    visited : list
        A list to keep track of the visited points.
    neighbors : dict
        A dictionary to store the neighbors of each point.
    X : numpy.ndarray
        The input data.
    labels : numpy.ndarray
        An array of cluster labels assigned to each data point.
    centroids : list
        A list of cluster centroids.

    Methods
    -------
    get_neighbors(sample)
        Get the neighbors of a point.
    divide_cluster(sample, neighbors)
        Recursively find all the points that belong to the same cluster.
    get_cluster_labels(cluster)
        Assign labels to all points in a cluster.
    fit(X)
        Cluster the input data.
    """

    def __init__(self, diss_func=euclidean_distance, epsilon=0.5, min_points=5):
        """
        Initialize the DBSCAN instance.

        Parameters
        ----------
        diss_func : function, optional, default: euclidean_distance
            Dissimilarity function used to calculate the distance between two data points.
        epsilon : float, optional, default: 0.5
            The radius within which the algorithm searches for neighbors.
        min_points : int, optional, default: 5
            The minimum number of neighbors required to form a cluster.
        """
        self.eps = epsilon
        self.min_points = min_points
        self.diss_func = diss_func
        self.visited = []
        self.neighbors = {}
        self.X = None
        self.labels = None
        self.centroids = []

    def get_neighbors(self, sample):
        """
        Get the neighbors of a point.

        Parameters
        ----------
        sample : int
            The index of the point.

        Returns
        -------
        neighbors : numpy.ndarray
            An array of neighboring points.
        """
        ids = np.arange(len(self.X))
        neighbors = np.array([i for i in ids[ids != sample] if self.diss_func(self.X[sample], self.X[i]) < self.eps])
        return neighbors

    def divide_cluster(self, sample, neighbors):
        """
        Given a sample and its neighboring samples, this function recursively expands the cluster
        until it has reached its maximum size.

        Parameters:
        -----------
        sample: int
            The index of the sample under consideration.
        neighbors: ndarray
            The indices of the neighboring samples of the given sample.

        Returns:
        --------
        cluster: list
            The list of indices that belong to the cluster under consideration.
        """
        cluster = [sample]
        for i in neighbors:
            if i not in self.visited:
                self.visited.append(i)
                self.neighbors[i] = self.get_neighbors(i)
                if len(self.neighbors[i]) >= self.min_points:
                    # in case it brings new points, searching recursively
                    new_cluster = self.divide_cluster(i, self.neighbors[i])
                    cluster = cluster + new_cluster
                else:
                    # in case it does not bring new points
                    cluster.append(i)
        return cluster

    def get_cluster_labels(self, cluster):
        """
        Given a cluster, this function returns an array of labels such that each sample in the
        dataset is assigned to one of the clusters or is classified as noise.

        Parameters:
        -----------
        cluster: list
            A list of lists of indices that belong to the different clusters.

        Returns:
        --------
        labels: ndarray
            An array of cluster labels where -1 indicates noise and other non-negative integers
            correspond to the different clusters.
        """
        labels = np.full(shape=self.X.shape[0], fill_value=-1)
        for i in range(len(cluster)):
            for j in cluster[i]:
                labels[j] = i
        return labels

    def fit(self, X):
        """
        Given a dataset X, this function finds all the clusters in the data using DBSCAN.

        Parameters:
        -----------
        X: ndarray
            The dataset to be clustered.

        Returns:
        --------
        None
        """
        self.X = np.array(X)
        new_cluster = []
        n_samples = np.shape(self.X)[0]
        for sample in range(n_samples):
            if sample not in self.visited:
                self.neighbors[sample] = self.get_neighbors(sample)
                if len(self.neighbors[sample]) >= self.min_points:
                    self.visited.append(sample)
                    new_cluster.append(self.divide_cluster(sample, self.neighbors[sample]))
        if len(new_cluster) == 0:
            print("Couldn't find any clusters.")
        self.labels = self.get_cluster_labels(new_cluster)
