import numpy as np
from sklearn.base import clone, BaseEstimator
from sklearn import metrics, ensemble


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
