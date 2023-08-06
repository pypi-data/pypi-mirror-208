import numpy as np
import pytest
from myclustering.pca.pca import PCA

def test_pca_fit_transform():
    # Generate sample data
    np.random.seed(0)
    X = np.random.rand(100, 5)

    # Define the number of principal components
    n_components = 3

    # Create PCA object
    pca = PCA(n_components=n_components)
    
    # Fit and transform the data
    pca.fit(X)
    transformed_X = pca.transform(X)

    # Check the shape of the transformed data
    assert transformed_X.shape == (100, n_components)

def test_pca_components_mean():
    # Generate sample data
    np.random.seed(0)
    X = np.random.rand(100, 5)

    # Define the number of principal components
    n_components = 3

    # Create PCA object
    pca = PCA(n_components=n_components)

    # Fit the data
    pca.fit(X)

    # Check the shape of the components
    assert pca.components.shape == (n_components, 5)

    # Check the shape of the mean
    assert pca.mean.shape == (5,)

