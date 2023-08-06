import numpy as np
import sklearn.metrics as sklearn_metrics
import math

def inertia_score(X, labels, return_type='curve'): #or 'value'
    """Also known as Elbow method. It is the same of scikit-learn's KMeans.inertia_, but it works also in case of only one label."""

    inertia = 0
    for label in set(labels):
        X_cluster = X[labels == label, :]
        centroid = np.mean(X_cluster, axis=0)
        inertia += np.sum((X_cluster - centroid) ** 2)

    if return_type=='value':
        #return max second derivative
        return np.argmax([inertia[i + 1] + inertia[i - 1] - 2 * inertia[i] for (i, x) in enumerate(inertia[1:-1])])+2

    return inertia

def calinski_harabasz_score(X, labels, return_type='curve'):
    """Wrapper function of Scikit-learn's calinski_harabasz_score. The only difference is it doesn't throw an error where there is only one label."""

    if len(set(labels)) == 1:
        return float("NaN")
    else:
        curve= sklearn_metrics.calinski_harabasz_score(X, labels)

    if return_type=='curve':
        return np.argmax(curve)
    return curve

def davies_bouldin_score(X, labels, return_type='curve'):
    """Wrapper function of Scikit-learn's davies_bouldin_score. The only difference is it doesn't throw an error where there is only one label."""

    if len(set(labels)) == 1:
        return float("NaN")
    else:
        curve= sklearn_metrics.davies_bouldin_score(X, labels)

    if return_type=='curve':
        return np.argmin(curve)
    return curve

def silhouette_score(X, labels, return_type='curve'):
    """Wrapper function of Scikit-learn's silhouette_score. The only difference is it doesn't throw an error where there is only one label."""

    if len(set(labels)) == 1:
        return float("NaN")
    else:
        curve= sklearn_metrics.silhouette_score(X, labels)

    if return_type=='curve':
        return np.argmax(curve)
    return curve

def bic_score(X: np.ndarray, labels: np.array, return_type='curve'):
    """
    BIC (Bayesian Information Criterion) score for the goodness of fit of clusters.
    This Python function is translated from the Golang implementation by the author of the paper.
    The original code is available here: https://github.com/bobhancock/goxmeans/blob/a78e909e374c6f97ddd04a239658c7c5b7365e5c/km.go#L778
    """

    n_points = len(labels)
    n_clusters = len(set(labels))
    n_dimensions = X.shape[1]

    n_parameters = (n_clusters - 1) + (n_dimensions * n_clusters) + 1

    loglikelihood = 0
    for label_name in set(labels):
        X_cluster = X[labels == label_name]
        n_points_cluster = len(X_cluster)
        centroid = np.mean(X_cluster, axis=0)
        variance = np.sum((X_cluster - centroid) ** 2) / (len(X_cluster) - 1)
        loglikelihood += \
            n_points_cluster * np.log(n_points_cluster) \
            - n_points_cluster * np.log(n_points) \
            - n_points_cluster * n_dimensions / 2 * np.log(2 * math.pi * variance) \
            - (n_points_cluster - 1) / 2

    curve = loglikelihood - (n_parameters / 2) * np.log(n_points)

    if return_type=='curve':
        return np.argmax(curve)
    return curve