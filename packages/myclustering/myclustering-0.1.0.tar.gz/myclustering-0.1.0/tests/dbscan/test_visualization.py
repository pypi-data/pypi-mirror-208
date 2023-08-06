import numpy as np
from myclustering.dbscan.visualization import plot_dbscan_pca

def test_plot_dbscan_pca():
    # Generate sample data
    np.random.seed(0)
    X = np.random.rand(100, 2)

    # Test the function with different parameters
    epsilon = 0.5
    min_points = 5
    plot_dbscan_pca(X, epsilon, min_points)

    epsilon = 0.2
    min_points = 10
    plot_dbscan_pca(X, epsilon, min_points)