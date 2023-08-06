import networkx as nx
import pandas as pd
import numpy as np
from sklearn import decomposition, manifold
umap = None


def x_reduce_dim_2d(df, method='umap', **kwargs):
    """
    Various ways of reducing to 2D
    Note: can pass df.T to get feature similarity
    """

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    if method == 'spring':
        G = nx.Graph(df.T.corr())
        pos = nx.spring_layout(G)
        df_2d = pd.DataFrame(pos).T

    elif method == 'umap':
        global umap
        if umap is None:
            import umap

        pos = umap.UMAP(**kwargs).fit_transform(df)
        df_2d = pd.DataFrame(pos)

    elif method == 'tsne':
        pos = manifold.TSNE(**kwargs).fit_transform(df)
        df_2d = pd.DataFrame(pos)

    elif method == 'pca':
        pos = decomposition.PCA(n_components=2, **kwargs).fit_transform(df)
        df_2d = pd.DataFrame(pos)

    else:
        raise ValueError(method)

    df_2d.columns = ['x', 'y']
    return df_2d


def x_inspect_cols(df):
    """
    Go over columns, get general idea of what they contain
    """

    for col_name in df.columns:
        sa_orig = df[col_name]
        sa = sa_orig.dropna()
        num_unique = len(sa.unique())
        topk = (sa.value_counts() / len(sa)).iloc[:5]
        topk_text = ", ".join([ f"{k}={100*v:.2f}%" for k,v in topk.items()])
        prec_na = 1 - len(sa)/len(sa_orig)
        print(f"{col_name}: dtype={sa.dtype} na={100*prec_na:.1f}% #unique={num_unique} top5={topk_text}")


def x_corr_with_target(df, target):
    """
    Go over columns, see how well they correlate with target
    """

    df, new_target = x_prep_col(df, target, on_na='drop')
    assert len(new_target) == 1, new_target
    if target != new_target:
        print(f'New Target: {target} ==> {new_target}')

    target = new_target[0]

    rows = []
    for col_name in df.columns:
        if col_name == target:
            continue

        df_sub = df[[col_name, target]].dropna()
        df_sub, new_cols = x_prep_col(df_sub, col_name)
        if len(new_cols) == 0:
            print(f"{col_name}: SKIPPED")
            continue

        elif len(new_cols) == 1:
            new_col = new_cols[0]
            corr = np.corrcoef(df_sub[new_col], df_sub[target])[0, 1]
            print(f"{new_col}: {corr}")
            rows.append({'orig_col': col_name, 'new_col': new_col, 'corr': corr, 'abs_corr': abs(corr)})

        else:
            print(f"{col_name}:")
            for new_col in new_cols:
                corr = np.corrcoef(df_sub[new_col], df_sub[target])[0, 1]
                print(f"   {new_col}: {corr}")
                rows.append({'orig_col': col_name, 'new_col': new_col, 'corr': corr, 'abs_corr': abs(corr)})

    df_corr = pd.DataFrame(rows)
    df_corr = df_corr.sort_values('abs_corr', ascending=False).reset_index(drop=True)
    return df_corr


def x_prep_df(df, target=None, on_na='auto'):
    """
    Go over columns, prepare for modeling (fill NA, dummy vars, etc.)
    NOTE: drops NA for target col, does "auto" for others
    """
    df = df.copy()

    new_target = None
    if target:
        df, new_target = x_prep_col(df, target, on_na='drop', inplace=True)
        assert len(new_target) == 1
        new_target = new_target[0]

    for col_name in df.columns:
        if col_name == new_target:
            continue

        df, _ = x_prep_col(df, col_name, on_na=on_na)

    if target is None:
        return df

    return df, new_target


def x_prep_col(df, col_name, on_na='auto', inplace=False):
    """
    prepare a column for modeling (fill NA, dummy vars, etc)
    """

    df = df.copy()
    new_cols = [col_name]

    if on_na == 'auto':
        if pd.api.types.is_float_dtype(df[col_name]):
            on_na = 'mean'
        elif pd.api.types.is_numeric_dtype(df[col_name]):
            on_na = 'median'
        else:
            on_na = 'na_value'

    if on_na == 'drop':
        df = df.dropna(subset=[col_name])

    elif on_na == 'mode':
        mode = df[col_name].value_counts().index.values[0]
        df[col_name] = np.where(df[col_name].isna(), mode, df[col_name])

    elif on_na == 'mean':
        mean = df[col_name].mean()
        df[col_name] = np.where(df[col_name].isna(), mean, df[col_name])

    elif on_na == 'median':
        median = df[col_name].median()
        df[col_name] = np.where(df[col_name].isna(), median, df[col_name])

    elif on_na == 'na_value':
        df[col_name] = np.where(df[col_name].isna(), 'NA', df[col_name])

    else:
        raise ValueError(on_na)

    if not pd.api.types.is_string_dtype(df[col_name]):
        return df, new_cols

    sa_col = df[col_name]
    unique_vals = np.unique(sa_col)
    num_unique = len(unique_vals)
    if num_unique == 1:
        del df[col_name]
        new_cols = []

    elif num_unique == 2:
        val_sel = sa_col.value_counts().index.values[0]
        new_val = (sa_col == val_sel).astype(int)
        if inplace:
            df[col_name] = new_val

        else:
            new_col_name = f"{col_name}_{val_sel}"
            new_cols = [new_col_name]
            df[new_col_name] = new_val
            del df[col_name]

    else:
        assert inplace is False, f"{col_name}: can't do inplace with multiple categorical values ({num_unique} unique)"

        new_cols = []
        for val_sel in unique_vals:
            new_val = (sa_col == val_sel).astype(int)
            new_col_name = f"{col_name}_{val_sel}"
            new_cols.append(new_col_name)
            df[new_col_name] = new_val

        del df[col_name]

    return df, new_cols
