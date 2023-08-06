import datetime as dt
from . import xpd, xnp, xplt

MIN_TIME = dt.datetime.min.time()


def x_monkey_patch(aggressive=False):
    xpd.monkey_patch(aggressive=aggressive)
    xnp.monkey_patch()
    xplt.monkey_patch()


def split_X_y(df, target):
    df = df.copy()
    y = df[target]
    del df[target]
    return df, y


def date_to_datetime(d):
    return dt.datetime.combine(d, MIN_TIME)
