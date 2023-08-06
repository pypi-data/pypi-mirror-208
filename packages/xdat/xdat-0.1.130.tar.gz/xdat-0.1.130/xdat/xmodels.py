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


class WeightedNeighbors:
    def __init__(self, clf, scale=True, n_iter=100):
        self.clf = clf
        self.scale = scale
        self.n_iter = n_iter
        self.scaler = preprocessing.StandardScaler()
        self.feature_weights = None

    def clone(self):
        clf = WeightedNeighbors(self.clf, scale=self.scale, n_iter=self.n_iter)
        if self.scale:
            clf.scaler = self.scaler.copy()

        clf.feature_weights = self.feature_weights
        return clf

    def _apply_weights(self, X, feature_weights=None):
        feature_weights = feature_weights or self.feature_weights


    def fit(self, X, y=None):
        if self.scale:
            X = self.scaler.fit_transform(X)

        def objective(trial):
            _X = X.copy()
            features = []
            weights = []
            for idx in range(X.shape[1]):
                include_p = trial.suggest_int(f"include_{idx}", 0, 1)
                if include_p:
                    features.append(idx)
                    weight = trial.suggest_float(f"weight_{idx}", 1, 1e3, log=True)
                    weights.append(weight)

            if len(features) == 0:
                return np.inf

            _X = X[features].copy()
            for idx, w in enumerate(weights):
                _X[idx] *= w

            _clf = clone(self.clf)
            _clf.fit(X, y=y)

            metrics.log_loss(y, _clf.predict_proba(_X), eps=1e-15)
            return

        study = optuna.create_study()
        study.optimize(objective, n_trials=self.n_iter)

        bp = study.best_params.copy()

