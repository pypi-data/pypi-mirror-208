import numpy as np
import pytest
from myclustering.kmeans.elbow import elbow_method

def test_elbow_method():
    # Generate sample data
    np.random.seed(0)
    X = np.random.rand(100, 2)

    # Test the function with different parameters
    max_clusters = 10
    elbow_method(X, max_clusters)

    max_clusters = 5
    elbow_method(X, max_clusters)