import numpy as np 
from myclustering.kmeans.kmeans import euclidean_distance


def silhouette_score(X, kmeans):
    """
    Calculates the Silhouette Score for a given dataset and a KMeans clustering model.

    Parameters:
    -----------
    X : numpy.ndarray
        Input data, where each row corresponds to a sample and each column corresponds to a feature.
    kmeans : KMeans
        A KMeans clustering model to evaluate.

    Returns:
    --------
    float
        The Silhouette Score for the given dataset and KMeans model.
    """

    # Fit the KMeans model to the input data and get the labels
    labels = kmeans.fit(X)

    # Compute the pairwise Euclidean distances between all samples in the input data
    n_samples = len(X)
    distances = np.zeros((n_samples, n_samples))
    for i in range(n_samples):
        for j in range(n_samples):
            distances[i][j] = euclidean_distance(X[i], X[j])

    # Compute the silhouette score for each sample
    silhouette_vals = np.zeros(n_samples)
    for i in range(n_samples):
        # Compute the mean distance between the i-th sample and all other samples in the same cluster
        a = np.mean(distances[i][labels == labels[i]])
   
        # Compute the minimum mean distance between the i-th sample and all other samples in different clusters
        b = np.inf
        for j in range(n_samples):
            if labels[j] != labels[i]:
                b = min(b, np.mean(distances[i][labels == labels[j]]))
        
        if a == 0 or b == 0:
            silhouette_vals[i] = 0
        else:
            silhouette_vals[i] = (b - a) / max(a, b)
            
    # Compute the mean Silhouette Score for all samples
    return np.mean(silhouette_vals)
