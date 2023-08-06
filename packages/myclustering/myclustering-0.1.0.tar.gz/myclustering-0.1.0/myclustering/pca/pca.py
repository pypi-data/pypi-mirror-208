"""Principal Component Analysis (PCA) module.

This module provides a class for performing PCA on data matrices. PCA is a
dimensionality reduction technique that seeks to transform the original data into
a lower-dimensional space by identifying a new set of orthogonal axes (principal
components) that capture the maximum amount of variance in the data.

Classes:
    PCA: A class for performing PCA on data matrices.
"""

import numpy as np


class PCA:

    """
    Principal Component Analysis (PCA) is a technique used to reduce the dimensionality
    of high-dimensional datasets while retaining the most important information.
    This class performs PCA on a dataset and transforms it to the specified number of principal components.
    
    Parameters
    ----------
    n_components : int
        The number of principal components to retain.
    
    Attributes
    ----------
    n_components : int
        The number of principal components to retain.
    components : ndarray of shape (n_components, n_features)
        The retained principal components.
    mean : ndarray of shape (n_features,)
        The mean of the dataset.
    
    Methods
    -------
    fit(X)
        Fit the PCA model on the dataset X.
    transform(X)
        Transform the dataset X to the specified number of principal components.
    """
    
    def __init__(self, n_components):
        self.n_components = n_components
        self.components = None
        self.mean = None

    def fit(self, X):
        """
        Fit the PCA model on the dataset X.
        
        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            The input data.
        """
        # Mean centering
        self.mean = np.mean(X, axis=0)
        X = X - self.mean
        # covariance, function needs samples as columns
        cov = np.cov(X.T)
        # eigenvalues, eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(cov)
        # -> eigenvector v = [:,i] column vector, transpose for easier calculations
        # sort eigenvectors
        eigenvectors = eigenvectors.T
        idxs = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idxs]
        eigenvectors = eigenvectors[idxs]
        # store first n eigenvectors
        self.components = eigenvectors[0:self.n_components]

    def transform(self, X):
        """
        Transform the dataset X to the specified number of principal components.
        
        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            The input data.
            
        Returns
        -------
        ndarray of shape (n_samples, n_components)
            The transformed dataset with the specified number of principal components.
        """
        # project data
        X = X - self.mean
        return np.dot(X, self.components.T)
