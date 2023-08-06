from sklearn.neighbors import NearestNeighbors


class DistributedNearestNeighbors:

    def __init__(self, nb_splits,  n_neighbors=5, radius=1.0, algorithm='auto', leaf_size=30, metric='minkowski', p=2, metric_params=None, n_jobs=None):
        self.nb_split=nb_splits
        self.nns=[NearestNeighbors(n_neighbors=n_neighbors, radius=radius, algorithm=algorithm, leaf_size=leaf_size, metric=metric, p=p, metric_params=metric_params, n_jobs=n_jobs) for n in range(self.nb_split)]

    def split(self, df,  n):

        k, m = divmod(len(df), n)

        return [df[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


    def fit(self, X, y=None):
        for nn in self.nns:
            nn.metric=self.metric

        dfs=self.split(X, self.nb_split)
        [nn.fit(dfs[i]) for i, nn in enumerate(self.nns)]


    @property
    def metric(self):
        return self._metric
    @metric.setter
    def metric(self, m):
        self._metric=m

    def kneighbors(self, X, return_distance=False):
        self.results=[nn.kneighbors(X) for nn in self.nns]

        return self.results