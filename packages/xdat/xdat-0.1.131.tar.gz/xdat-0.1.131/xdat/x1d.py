import inspect
import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
import numpy as np
from scipy.optimize import curve_fit
from . import xstats


def array_col_to_wide(df, array_col, prefix=None, n_jobs=1):
    if prefix is None:
        prefix = f"{array_col}"

    def get_row(row):
        a = row[array_col]
        del row[array_col]
        for idx, v in enumerate(a):
            row[f"{prefix}_{idx}"] = v
        return row

    all_rows = Parallel(n_jobs=n_jobs)(delayed(get_row)(r[1]) for r in tqdm(df.iterrows(), total=len(df)))
    df_all = pd.DataFrame(all_rows)
    return df_all


class CurveFit:
    def __init__(self, func, maxfev=500000):
        """
        func's params: x + params to fit
        eg: lambda x, a, b: a + b*x
        """

        self.func = func
        self.maxfev = maxfev
        self.num_params = len(inspect.signature(self.func).parameters)
        self.coefs = None
        self.cov = None
        self.x_train = None
        self.y_train = None
        self.y_pred = None
        self.stats = None

    def fit(self, y, x=None):
        y = np.array(y)
        if x is None:
            x = np.arange(len(y))
        else:
            x = np.array(x)

        self.x_train = x
        self.y_train = y

        self.coefs, self.cov = curve_fit(self.func, x, y, maxfev=self.maxfev)
        self.y_pred = self.predict(x)
        self.stats = xstats.x_model_pred_stats(self.y_pred, y, k=self.num_params-1, is_classification=False)

    def predict(self, x):
        y_pred = self.func(x, *self.coefs)
        if isinstance(y_pred, float) or len(y_pred) == 1:
            y_pred = np.ones(len(x)) * y_pred
        return y_pred

    def fit_predict(self, y, x=None):
        self.fit(y, x=x)
        return self.predict(self.x_train)


def x_best_curve_fit(y, funcs, x=None, maxfev=500000):
    best_cf = None
    for func in funcs:
        cf = CurveFit(func, maxfev=maxfev)
        cf.fit(y, x=x)
        if best_cf is None or cf.stats.p_value < best_cf.stats.p_value:
            best_cf = cf

    return best_cf

