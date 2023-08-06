import numpy as np
import pytest
from myclustering.kmeans.kmeans import KMeans, euclidean_distance

def test_euclidean_distance():
    x1 = np.array([1, 2, 3])
    x2 = np.array([4, 5, 6])
    assert euclidean_distance(x1, x2) == pytest.approx(5.196152422706632, abs=1e-6)

    x1 = np.array([0, 0, 0])
    x2 = np.array([0, 0, 0])
    assert euclidean_distance(x1, x2) == pytest.approx(0, abs=1e-6)

    x1 = np.array([1, 2, 3])
    x2 = np.array([-1, -2, -3])
    assert euclidean_distance(x1, x2) == pytest.approx(7.483314773547882, abs=1e-6)

def test_kmeans_fit():
    # Generate sample data
    np.random.seed(0)
    X = np.random.rand(100, 2)

    # Initialize KMeans with K=3
    kmeans = KMeans(K=3, max_iters=100, plot_steps=False)
    labels = kmeans.fit(X)

    # Assert the number of clusters is correct
    assert len(kmeans.centroids) == 3
    assert len(kmeans.clusters) == 3

    # Assert the labels are assigned correctly
    assert len(labels) == 100
    assert set(labels) == {0, 1, 2}


def test_kmeans_plot():
    # Generate sample data
    np.random.seed(0)
    X = np.random.rand(100, 2)

    # Initialize KMeans with K=3 and plot_steps=True
    kmeans = KMeans(K=3, max_iters=100, plot_steps=True)
    labels = kmeans.fit(X)

    # No assertions needed for the plot function as it only displays the plot
