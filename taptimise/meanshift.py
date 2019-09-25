import numpy as np
from sklearn.cluster import MiniBatchKMeans


def partition(houses, n_clusters=1):
    hs = np.asarray(houses)
    ms = MiniBatchKMeans(n_clusters=n_clusters)
    labels = ms.fit_predict(hs[::, :2:])

    batches = [[] for _ in range(n_clusters)]

    for h, l in zip(houses, labels):
        batches[l].append(h)

    return batches
