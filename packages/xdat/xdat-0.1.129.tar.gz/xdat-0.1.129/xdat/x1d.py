import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed


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
