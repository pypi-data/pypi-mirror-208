import numpy as np
import pytest
from myclustering.kmeans.kmeans import KMeans
from myclustering.kmeans.silhouette import silhouette_score

def test_silhouette_score():
    # Generate sample data
    np.random.seed(0)
    X = np.random.rand(100, 2)

    # Initialize KMeans with K=3
    kmeans = KMeans(K=3, max_iters=100, plot_steps=False)

    # Compute the Silhouette Score
    score = silhouette_score(X, kmeans)

    # Assert the score is within the range [-1, 1]
    assert -1 <= score <= 1
