import numpy as np
import pytest
from myclustering.kmeans.visualization import plot_kmeans_pca

def test_plot_kmeans_pca():
    # Generate sample data
    np.random.seed(0)
    X = np.random.rand(100, 3)

    # Define the number of clusters
    n_clusters = 3

    # Call the function
    plot_kmeans_pca(X, n_clusters)

    # No assertions for visualization functions, but make sure the plot is displayed without errors
