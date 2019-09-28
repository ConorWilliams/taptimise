import numpy as np
from sklearn.cluster import KMeans, SpectralClustering


def partition(houses, n_clusters=1):
    hs = np.asarray(houses)
    ms = KMeans(n_clusters=n_clusters)
    # ms = SpectralClustering(n_clusters=n_clusters,
    #                         eigen_solver='arpack', affinity="nearest_neighbors")
    labels = ms.fit_predict(hs[::, :2:])

    batches = [[] for _ in range(len(np.unique(labels)))]

    for h, l in zip(houses, labels):
        batches[l].append(h)

    return batches
