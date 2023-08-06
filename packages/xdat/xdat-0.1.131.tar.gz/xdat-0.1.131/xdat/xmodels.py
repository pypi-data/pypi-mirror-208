import numpy as np
import optuna
from sklearn.base import clone, BaseEstimator
from sklearn import metrics, ensemble, neighbors, preprocessing


def MonotonicClassifier(*args, **kwargs):
    return ensemble.HistGradientBoostingClassifier(*args, monotonic_cst=[1, -1], **kwargs)


class OrdinalClassifier(BaseEstimator):
    """
    Based on classifier that returns binary probability, builds a bunch of classifiers that together solve the ordinal classifier problem.

    Credits:
      https://www.cs.waikato.ac.nz/~eibe/pubs/ordinal_tech_report.pdf
      https://stackoverflow.com/questions/57561189/multi-class-multi-label-ordinal-classification-with-sklearn
    """

    def __init__(self, clf):
        """
        :param clf: binary classifier with 'predict_proba()'
        """

        self.clf = clf
        self.clfs = {}
        self.unique_class = None

    def fit(self, X, y):
        self.unique_class = np.sort(np.unique(y))
        assert self.unique_class.shape[0] > 2, 'looks like a binary problem'

        for i in range(self.unique_class.shape[0]-1):
            # for each k - 1 ordinal value we fit a binary classification problem
            binary_y = (y > self.unique_class[i]).astype(np.uint8)
            clf = clone(self.clf)
            clf.fit(X, binary_y)
            self.clfs[i] = clf

    def predict_proba(self, X):
        clfs_predict = {k: self.clfs[k].predict_proba(X) for k in self.clfs}
        predicted = []
        for i, y in enumerate(self.unique_class):
            if i == 0:
                # V1 = 1 - Pr(y > V1)
                predicted.append(1 - clfs_predict[i][:,1])
            elif i in clfs_predict:
                # Vi = Pr(y > Vi-1) - Pr(y > Vi)
                 predicted.append(clfs_predict[i-1][:,1] - clfs_predict[i][:,1])
            else:
                # Vk = Pr(y > Vk-1)
                predicted.append(clfs_predict[i-1][:,1])
        return np.vstack(predicted).T

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)

    def score(self, X, y, sample_weight=None):
        _, indexed_y = np.unique(y, return_inverse=True)
        return metrics.accuracy_score(indexed_y, self.predict(X), sample_weight=sample_weight)


class KNeighborsMixinTrain(neighbors._base.KNeighborsMixin):
    _orig_kneighbors = neighbors._base.KNeighborsMixin.kneighbors

    def _train_kneighbors(self, X=None, n_neighbors=None, return_distance=True):
        n_neighbors = n_neighbors or self.n_neighbors
        res = self._orig_kneighbors(X, n_neighbors=n_neighbors+1, return_distance=return_distance)
        if return_distance:
            neigh_dist, neigh_ind = res
            neigh_dist = neigh_dist[:, 1:]
            neigh_ind = neigh_ind[:, 1:]
            return neigh_dist, neigh_ind

        neigh_ind = res
        neigh_ind = neigh_ind[:, 1:]
        return neigh_ind

    def predict_train(self, X):
        self.kneighbors = self._train_kneighbors
        try:
            return self.predict(X)
        finally:
            self.kneighbors = self._orig_kneighbors

    def predict_proba_train(self, X):
        self.kneighbors = self._train_kneighbors
        try:
            return self.predict_proba(X)
        finally:
            self.kneighbors = self._orig_kneighbors

    def score_train(self, X, y):
        self.kneighbors = self._train_kneighbors
        try:
            return self.score(X, y)
        finally:
            self.kneighbors = self._orig_kneighbors


class KNeighborsClassifierWithTrain(neighbors.KNeighborsClassifier, KNeighborsMixinTrain):
    pass


class KNeighborsRegressorWithTrain(neighbors.KNeighborsRegressor, KNeighborsMixinTrain):
    pass


class WeightedNeighbors:
    def __init__(self, clf, scale=True, n_iter=100, n_jobs=-1):
        assert isinstance(clf, KNeighborsMixinTrain), "Must used a model with ability to predict on training data"

        self.clf = clf
        self.scale = scale
        self.n_iter = n_iter
        self.n_jobs = n_jobs
        self.scaler = preprocessing.StandardScaler()
        self.feature_weights = None

    def clone(self):
        clf = WeightedNeighbors(self.clf, scale=self.scale, n_iter=self.n_iter)
        if self.scale:
            clf.scaler = self.scaler.copy()

        clf.feature_weights = self.feature_weights
        return clf

    def _apply_weights(self, X, feature_weights=None):
        feature_weights = feature_weights if feature_weights is not None else self.feature_weights

        idxs = feature_weights > 0
        X = X[:, idxs]

        feature_weights = feature_weights[idxs]
        for idx, w in enumerate(feature_weights):
            X[:, idx] *= w

        return X

    def transform(self, X):
        if self.scale:
            X = self.scaler.transform(X)

        X = self._apply_weights(X)
        return X

    def fit(self, X, y=None):
        if self.scale:
            X = self.scaler.fit_transform(X)

        def objective(trial):
            _X = X.copy()
            weights = []
            for idx in range(X.shape[1]):
                include_p = trial.suggest_int(f"include_{idx}", 0, 1)
                if include_p:
                    weight = trial.suggest_float(f"weight_{idx}", 1, 8)
                    weights.append(weight)
                else:
                    weights.append(0)

            weights = np.array(weights)
            # print(weights)
            if (weights > 0).sum() == 0:
                return -1*np.inf

            _X = self._apply_weights(_X, feature_weights=weights)

            _clf = clone(self.clf)
            _clf.fit(_X, y=y)

            score = _clf.score_train(_X, y)
            return score

        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=self.n_iter, n_jobs=self.n_jobs)

        bp = study.best_params.copy()
        weights = []
        for idx in range(X.shape[1]):
            if bp[f'include_{idx}'] == 0:
                weights.append(0)
            else:
                weights.append(bp[f'weight_{idx}'])

        weights = np.array(weights)
        self.feature_weights = weights
        _X = self._apply_weights(X)
        self.clf.fit(_X, y)


if __name__ == "__main__":
    from sklearn.datasets import fetch_california_housing
    import pandas as pd

    housing_data = fetch_california_housing()

    descr = housing_data['DESCR']
    feature_names = housing_data['feature_names']
    data = housing_data['data']
    target = housing_data['target']
    df = pd.DataFrame(dict(zip(feature_names, data.T)))

    clf = WeightedNeighbors(KNeighborsRegressorWithTrain(), n_iter=1000, n_jobs=-1)
    clf.fit(df, target)
    df2 = clf.transform(df)
    clf2 = KNeighborsRegressorWithTrain()
    clf2.fit(df2, target)
    print(clf2.score_train(df2, target))

    df = df[['Latitude', 'Longitude']]
    clf = neighbors.KNeighborsRegressor()
    clf.fit(df, target)
    clf2 = KNeighborsRegressorWithTrain()
    clf2.fit(df, target)
    print(clf2.score_train(df, target))
    # metrics.log_loss(target, clf.predict(df), eps=1e-15)


    print('hi')