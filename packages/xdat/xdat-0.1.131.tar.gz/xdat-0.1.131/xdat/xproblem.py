import math
import numpy as np
import pandas as pd
from collections import namedtuple
from contextlib import contextmanager
from sklearn import model_selection, pipeline, metrics
from sklearn.base import clone
try:
    from glm.glm import GLM
    from glm.simulation import Simulation
except ImportError:
    GLM = Simulation = None

from tqdm import tqdm
from joblib import Parallel, delayed
from . import xutils


Metric = namedtuple('Metric', ['name', 'func', 'args'])
METRICS = {
    'AUC': Metric(name='AUC', func=metrics.roc_auc_score, args=['target', 'prob_1']),
    'R2': Metric(name='R2', func=metrics.r2_score, args=['pred', 'target']),
    'MAPE': Metric(name='MAPE', func=metrics.mean_absolute_percentage_error, args=['pred', 'target']),
    'MAE': Metric(name='MAE', func=metrics.mean_absolute_error, args=['pred', 'target']),
    'MSE': Metric(name='MSE', func=metrics.mean_squared_error, args=['pred', 'target']),
    'MSLE': Metric(name='MSLE', func=metrics.mean_squared_log_error, args=['pred', 'target']),
    'BAL_ACC': Metric(name="BAL_ACC", func=metrics.balanced_accuracy_score, args=['pred', 'target'])
}

for k,v in list(METRICS.items()):
    METRICS[k.lower()] = v


CVSplit = namedtuple("CVSplit", ['df_train', 'df_test', 'df_val'])


def cv_split_prep(df, n_splits=12, stratify_on=None, group_on=None):
    df = df.sample(frac=1.).reset_index(drop=True)
    groups = df[group_on] if group_on else None
    y = df[stratify_on] if stratify_on else None

    if group_on is None:
        if n_splits == 'max':
            if not stratify_on:
                n_splits = len(df)
            else:
                n_splits = df.value_counts(stratify_on).min()
        elif isinstance(n_splits, str) and n_splits.startswith('max:'):
            max_limit = int(n_splits.split(':')[1])
            n_splits = min(len(df), max_limit)

        if stratify_on:
            kfold = model_selection.StratifiedKFold(n_splits=n_splits)

        else:
            kfold = model_selection.KFold(n_splits=n_splits)

    else:
        num_groups = len(np.unique(groups))
        if n_splits == 'max':
            n_splits = num_groups
        elif isinstance(n_splits, str) and n_splits.startswith('max:'):
            max_limit = int(n_splits.split(':')[1])
            n_splits = min(num_groups, max_limit)

        n_splits = min(n_splits, num_groups)

        if stratify_on:
            kfold = model_selection.StratifiedGroupKFold(n_splits=n_splits)

        else:
            kfold = model_selection.GroupKFold(n_splits=n_splits)

    return df, groups, y, kfold, n_splits


def cv_split(df, n_splits=12, stratify_on=None, group_on=None, val_size=0.0):
    df, groups, y, kfold, n_splits = cv_split_prep(df, n_splits=n_splits, stratify_on=stratify_on, group_on=group_on)

    for train_index, test_index in kfold.split(df, y=y, groups=groups):
        df_train = df.iloc[train_index].reset_index(drop=True)
        df_test = df.iloc[test_index].reset_index(drop=True)
        df_val = None

        if val_size:
            # assert not group_on, "Not yet implemented"

            stratify = df_train[stratify_on] if stratify_on else None
            df_train, df_val = model_selection.train_test_split(df_train, test_size=val_size, stratify=stratify)

        yield CVSplit(df_train=df_train, df_test=df_test, df_val=df_val)


CVFold = namedtuple("CVFold", ['clf', 'df_train', 'df_test', 'feature_names', 'df_val', 'tm', 'xym'])


class TargetManipulation:
    def __init__(self, kind=None):
        assert kind in [None, 'log'], kind
        self.kind = kind

    def __repr__(self):
        return f"<TargetManipulation kind={self.kind}>"

    def pre(self, y):
        if self.kind is None:
            return y
        elif self.kind == 'log':
            return np.log(y)

    def post(self, y):
        if self.kind is None:
            return y
        elif self.kind == 'log':
            return np.e**y


class XYManipulation:
    def __init__(self, as_numpy=False, framework='sklearn'):
        self.as_numpy = as_numpy
        self.framework = framework

    def transform(self, X, y=None):
        if self.as_numpy:
            X = X.to_numpy()
            if y is not None:
                y = y.to_numpy()

        if self.framework == 'py-glm':
            intercept = np.ones([X.shape[0], 1])
            X = np.concatenate([intercept, X], axis=1)

        if y is None:
            return X

        return X, y


def train_cv(df, target_col, clf, n_splits=12, stratify_on=None, group_on=None, ordered_split=False, del_cols=tuple(), feature_cols=tuple(), uid_col=None, sample_weight_col=None, eval_size=0.0, framework='auto', fit_params=None, target_manipulation=None, with_confidence=False, with_tqdm=True, as_numpy=False, n_jobs=1):
    # fix feature names...
    df.columns = [str(c) if isinstance(c, str) else c for c in df.columns]
    assert not (del_cols and feature_cols), "should only specify features or del columns"
    assert framework in ['auto', 'sklearn', 'lightgbm', 'py-glm'], framework

    if framework == 'auto':
        if GLM is not None and isinstance(clf, GLM):
            framework = 'py-glm'
        else:
            framework = 'sklearn'

    if eval_size:
        assert framework in ['lightgbm'], "need to specify proper framework param"
    else:
        eval_type = None

    if framework == 'py-glm':
        as_numpy = True

    keep_cols = None
    if feature_cols:
        keep_cols = list(feature_cols) + [target_col]

    fit_params = dict() if fit_params is None else fit_params

    del_cols = set(del_cols)
    if uid_col:
        del_cols.add(uid_col)
    if sample_weight_col:
        del_cols.add(sample_weight_col)
    del_cols = sorted(del_cols)

    xym = XYManipulation(as_numpy=as_numpy, framework=framework)
    tm = TargetManipulation(target_manipulation)

    def calc_fold(fold_num, split_data: CVSplit):
        try:
            clf_fold = clone(clf)
        except TypeError:
            clf_fold = clf.clone()

        df_train = split_data.df_train
        df_train_data = df_train.copy()
        df_val = split_data.df_val
        df_val_data = None
        if df_val is not None:
            df_val_data = df_val.copy()

        df_test = split_data.df_test
        df_test_data = df_test.copy()
        test_tmp_uid = df_test[uid_col] if uid_col else None
        sample_weight_train = df_train[sample_weight_col] if sample_weight_col else None
        sample_weight_eval = df_val[sample_weight_col] if sample_weight_col else None

        if ordered_split and group_on:
            assert n_splits == 'max'
            test_group = df_test[group_on].min()
            df_train = df_train[df_train[group_on] < test_group].reset_index(drop=True)
            assert (df_train[group_on] >= test_group).sum() == 0
            if len(df_train) == 0:
                return

        if del_cols:
            df_train_data = df_train.drop(columns=del_cols, errors='ignore')
            df_test_data = df_test.drop(columns=del_cols, errors='ignore')
            if df_val_data is not None:
                df_val_data = df_val_data.drop(columns=del_cols, errors='ignore')

        if keep_cols:
            df_train_data = df_train[keep_cols].copy()
            df_test_data = df_test[keep_cols].copy()
            if df_val_data is not None:
                df_val_data = df_val_data[keep_cols].copy()

        X_train, y_train = xutils.split_X_y(df_train_data, target_col)
        feature_names = X_train.columns
        y_train = tm.pre(y_train)
        X_train, y_train = xym.transform(X_train, y_train)

        X_eval, Y_eval = None, None
        if df_val_data is not None:
            X_eval, Y_eval = xutils.split_X_y(df_val_data, target_col)
            Y_eval = tm.pre(Y_eval)

        if sample_weight_train is not None:
            if eval_type == 'lightgbm':
                eval_set = [[X_eval, Y_eval]]
                clf_fold.fit(X_train, y_train, sample_weight=sample_weight_train, eval_set=eval_set, eval_sample_weight=sample_weight_eval, **fit_params)
            else:
                clf_fold.fit(X_train, y_train, sample_weight=sample_weight_train, **fit_params)

        else:
            if eval_type == 'lightgbm':
                eval_set = [[X_eval, Y_eval]]
                clf_fold.fit(X_train, y_train, eval_set=eval_set, **fit_params)
            else:
                clf_fold.fit(X_train, y_train, **fit_params)

        pred_train = clf_fold.predict(X_train)
        df_train['pred'] = tm.post(pred_train)

        def capture_predict_proba(df, X):
            if hasattr(clf_fold, "predict_proba"):
                prob_1 = clf_fold.predict_proba(X)
                if len(prob_1.shape) == 1:
                    pass
                elif prob_1.shape[1] == 1:
                    prob_1 = prob_1[:, 0]
                else:
                    prob_1 = prob_1[:, 1]

                df['prob_1'] = prob_1

        capture_predict_proba(df_train, X_train)

        if eval_type:
            pred_eval = clf_fold.predict(X_eval)
            df_val['pred'] = tm.post(pred_eval)
            if hasattr(clf_fold, "predict_proba"):
                prob_1 = clf_fold.predict_proba(X_eval)[:, 1]
                df_val['prob_1'] = prob_1

        X_test, y_test = xutils.split_X_y(df_test_data, target_col)
        X_test, y_test = xym.transform(X_test, y_test)

        pred = clf_fold.predict(X_test)
        df_test['pred'] = tm.post(pred)

        capture_predict_proba(df_test, X_test)

        if with_confidence:
            if xym.framework not in ['py-glm']:
                raise NotImplementedError("Only implemented with_confidence for: py-glm")

            sim = Simulation(clf_fold)
            new_clfs = sim.parametric_bootstrap(X_train, n_sim=with_confidence)

            def get_pred_conf(X):
                all_y = [clf.predict(X) for clf in new_clfs]
                all_y = [a for a in all_y if np.isnan(a).sum() == 0]
                all_y = [tm.post(a) for a in all_y]
                all_y = [y.reshape(y.shape + (1,)) for y in all_y]
                y = np.concatenate(all_y, axis=1)
                return [yy for yy in y]

            df_train['pred_conf'] = get_pred_conf(X_train)
            df_test['pred_conf'] = get_pred_conf(X_test)

            if df_val is not None:
                df_val['pred_conf'] = get_pred_conf(X_eval)

        df_test['fold_num'] = fold_num
        if uid_col:
            df_test[uid_col] = test_tmp_uid

        fold = CVFold(clf=clf_fold, df_train=df_train, df_test=df_test, feature_names=feature_names, df_val=df_val, tm=tm, xym=xym)

        return fold

    _, _, _, _, total = cv_split_prep(df, n_splits=n_splits, stratify_on=stratify_on, group_on=group_on)
    splits = cv_split(df, n_splits=n_splits, stratify_on=stratify_on, group_on=group_on, val_size=eval_size)

    if with_tqdm:
        tqdm_splits = tqdm(enumerate(splits), total=total)
    else:
        tqdm_splits = enumerate(splits)

    if n_jobs == 1:
        all_folds = [calc_fold(fold_num, split_data) for fold_num, split_data in tqdm_splits]

    else:
        all_folds = Parallel(n_jobs=n_jobs)(delayed(calc_fold)(fold_num, split_data) for fold_num, split_data in tqdm_splits)

    all_folds = [fold for fold in all_folds if fold is not None]

    df_test = pd.concat([i[2] for i in all_folds], ignore_index=True)
    df_test = df_test.reset_index(drop=True)
    return df_test, all_folds


def eval_test(df_test, eval_per=None, metric_list=None):
    """

    :type metrics: list[Metric|str]
    """

    df_test = df_test.copy()
    df_test['none'] = 'none'

    metric_list = [m if isinstance(m, Metric) else METRICS[m] for m in metric_list]

    if not isinstance(eval_per, list) and not isinstance(eval_per, tuple):
        eval_per = [eval_per]

    rows = []
    for curr_group in eval_per:
        if not curr_group:
            curr_group = 'none'

        for gval in df_test[curr_group].unique():
            df_g = df_test[df_test[curr_group] == gval]
            row = {m.name: m.func(*(df_g[arg] for arg in m.args)) for m in metric_list}
            row['cv_grouping'] = curr_group
            row['cv_group_key'] = str(gval)
            row['cv_group_size'] = len(df_g)
            rows.append(row)

    df_res = pd.DataFrame(rows)
    return df_res


def calc_feature_importances(folds, flat=False):
    rows = []
    fi_var = None
    for fold in folds:
        clf = fold.clf
        if isinstance(clf, pipeline.Pipeline):
            clf = clf[-1]

        if fi_var is None:
            for var in ['feature_importances_', 'coef_']:
                if hasattr(clf, var):
                    fi_var = var
                    break

            if not fi_var:
                print("Can't find in clf")
                return

        fi = getattr(clf, fi_var).flatten()
        fi_dict = dict(zip(fold.feature_names, fi))
        if flat:
            for k, v in fi_dict.items():
                rows.append({'feature_name': k, 'feature_importance': v})

        else:
            rows.append(fi_dict)

    df = pd.DataFrame(rows)
    return df


class ModelEnsemble:
    def __init__(self, all_folds, is_binary=True):
        self.is_binary = is_binary
        self.clfs = [f.clf for f in all_folds]

        fold0 = all_folds[0]
        assert isinstance(fold0, CVFold)
        self.tm = fold0.tm
        if is_binary:
            assert self.tm.kind is None, "can't do target manipulation with binary"

        self.xym = fold0.xym
        self.feature_names = fold0.feature_names

    def prepare_X(self, df):
        df = df[self.feature_names].copy()
        df.columns = [str(c) if isinstance(c, str) else c for c in df.columns]

        df = self.xym.transform(df)
        return df

    def predict(self, X):
        X = self.prepare_X(X)
        all_y = [clf.predict(X) for clf in self.clfs]
        all_y = [y.reshape(y.shape + (1,)) for y in all_y]
        Y = np.concatenate(all_y, axis=1)

        if self.is_binary:
            pred = [np.bincount(y).argmax() for y in Y]
        else:
            Y = self.tm.post(Y)
            pred = [np.mean(y) for y in Y]

        pred = np.array(pred)
        return pred

    def predict_binary(self, X, threshold=0.5):
        prob_1 = self.predict_proba(X)[:, 1]
        pred = prob_1 >= threshold
        return pred.astype(int)

    def predict_proba(self, X):
        y = self.predict_proba_distribution(X)
        proba = y.mean(axis=2)
        return proba

    def predict_proba_distribution(self, X):
        X = self.prepare_X(X)
        all_y = [clf.predict_proba(X) for clf in self.clfs]
        all_y = [y.reshape(y.shape + (1,)) for y in all_y]
        y = np.concatenate(all_y, axis=2)
        return y

    def predict_confidence(self, X, n_sim=1000, as_list=True):
        assert self.xym.framework == 'py-glm'
        X = self.prepare_X(X)

        num_per_clf = math.ceil(n_sim / len(self.clfs))
        all_clfs = []
        for clf in self.clfs:
            sim = Simulation(clf)

            new_clfs = sim.parametric_bootstrap(X, n_sim=num_per_clf)
            all_clfs.extend(new_clfs)

        all_y = [clf.predict(X) for clf in all_clfs]
        all_y = [a for a in all_y if np.isnan(a).sum() == 0]
        all_y = [self.tm.post(a) for a in all_y]
        all_y = [y.reshape(y.shape + (1,)) for y in all_y]
        y = np.concatenate(all_y, axis=1)

        if as_list:
            y = [i for i in y]
        return y


class ModelCVEnsembleBuilder(ModelEnsemble):
    """
    Builds an ensemble of models vs CV
    """

    def __init__(self):
        super().__init__(None)

        self.target_col = None
        self.uid_col = None
        self.del_cols = None
        self.df_train = None
        self.df_test = None
        self.df_eval = None
        self.all_folds = None

    def fit(self, df, target_col, clf, n_splits=12, stratify_on=None, group_on=None, ordered_split=False, del_cols=tuple(), uid_col=None, sample_weight_col=None, eval_size=0.0, eval_type=None, fit_params=None, with_tqdm=True, n_jobs=1):
        self.target_col = target_col
        self.uid_col = uid_col
        self.del_cols = del_cols
        self.df_test, self.all_folds = train_cv(df, target_col, clf, n_splits=n_splits, stratify_on=stratify_on, group_on=group_on, ordered_split=ordered_split, del_cols=del_cols, uid_col=uid_col, sample_weight_col=sample_weight_col, eval_size=eval_size, eval_type=eval_type, fit_params=fit_params, with_tqdm=with_tqdm, n_jobs=n_jobs)

        self.clfs = [f.clf for f in self.all_folds]

    def eval_cv_test(self, eval_per=None, metric_list=None):
        self.df_eval = eval_test(self.df_test, eval_per=eval_per, metric_list=metric_list)
        return self.df_eval

    def _transform(self, df):
        del_cols = list({self.target_col} | {self.uid_col} | set(self.del_cols))
        del_cols = [c for c in del_cols if c is not None]
        df2 = df.drop(columns=del_cols).copy()
        return df2

    def predict(self, X):
        X2 = self._transform(X)
        return super().predict(X2)

    def predict_proba(self, X):
        X2 = self._transform(X)
        return super().predict_proba(X2)




