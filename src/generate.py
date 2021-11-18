import pandas as pd

# Supported dataset generators
from sklearn.datasets import make_blobs
from sklearn.datasets import make_moons
from sklearn.datasets import make_circles
from sklearn.datasets import make_classification

def blobs(samples, centers, features):
    X, y = make_blobs(n_samples=samples, centers=centers, 
                        n_features=features)
    return _create_pd_dataframe(X, y)

def moons(samples, noise):
    X, y = make_moons(n_samples=samples, noise=noise)
    return _create_pd_dataframe(X, y)

def circles(samples, noise):
    X, y = make_circles(n_samples=samples, noise=noise)
    return _create_pd_dataframe(X, y)

def classification(samples, features, classes):
    X, y = make_classification(
        n_samples=samples, 
        n_features=features, 
        n_classes=classes,
        n_redundant=0, 
        n_informative=2, 
        n_clusters_per_class=1
        )
    return _create_pd_dataframe(X, y)

def _create_pd_dataframe(samples, label):
    df = pd.DataFrame(samples)
    df['label'] = label
    return df