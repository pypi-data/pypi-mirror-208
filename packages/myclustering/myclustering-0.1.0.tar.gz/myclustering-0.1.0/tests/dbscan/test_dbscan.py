import numpy as np
from sklearn.datasets import make_moons
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

from myclustering.dbscan.dbscan import DBSCAN


def test_dbscan_on_moons():
    # Test DBSCAN on moons dataset
    X, y = make_moons(n_samples=200, noise=0.05, random_state=0)

    dbscan = DBSCAN(epsilon=0.3, min_points=5)
    dbscan.fit(X)

    assert adjusted_rand_score(y, dbscan.labels) > 0.95




def test_dbscan_on_single_cluster():
    # Test DBSCAN on a dataset with only one cluster
    X = np.random.rand(200, 2)

    dbscan = DBSCAN(epsilon=0.5, min_points=5)
    dbscan.fit(X)

    assert len(np.unique(dbscan.labels)) == 1


def test_dbscan_on_noise():
    # Test DBSCAN on a dataset with only noise
    X = np.random.rand(200, 2)

    dbscan = DBSCAN(epsilon=0.01, min_points=5)
    dbscan.fit(X)

    assert len(np.unique(dbscan.labels)) == 1 and dbscan.labels[0] == -1
