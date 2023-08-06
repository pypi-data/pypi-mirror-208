from tqdm import tqdm
import multiprocessing
from joblib import Parallel, delayed


def x_on_iter(llist, calc_func, clear_nones=False, n_jobs=-1):
    if n_jobs == 1:
        all_items = [calc_func(i) for i in tqdm(llist, total=len(llist))]

    else:
        xtqdm = x_tqdm(llist, total=len(llist), n_jobs=n_jobs)
        all_items = Parallel(n_jobs=n_jobs)(delayed(calc_func)(i) for i in xtqdm)
        xtqdm.finished()

    if clear_nones:
        all_items = [i for i in all_items if i is not None]

    return all_items


def x_on_keys(ddict, keys, func, n_jobs=-1):
    all_keys = list(keys)
    xtqdm = x_tqdm(all_keys, total=len(all_keys))
    all_vals = Parallel(n_jobs=n_jobs)(delayed(func)(ddict[k]) for k in xtqdm)
    xtqdm.finished()
    new_dict = dict(zip(all_keys, all_vals))
    return new_dict


def x_reduce(llist, calc_func, reduce_func=max, n_jobs=-1):
    vals = x_on_iter(llist, calc_func, n_jobs=n_jobs)
    vals = [v for v in vals if v is not None]
    val = reduce_func(vals)
    return val


class x_tqdm(tqdm):
    """
    tqdm that handles parallel jobs better
    """

    def __init__(self, *args, n_jobs=1, **kwargs):
        if n_jobs == -1:
            n_jobs = multiprocessing.cpu_count()

        self.n_jobs = n_jobs
        self.is_finished = False
        super().__init__(*args, **kwargs)

    def finished(self):
        self.is_finished = True
        self.refresh()
        self.close()

    def close(self):
        pass

    def do_close(self):
        super().close()

    @property
    def format_dict(self):
        fd = super().format_dict

        if not self.is_finished:
            fd['n'] = max(fd['n']-self.n_jobs, 0)
        return fd

if __name__ == "__main__":
    import time
    x = x_tqdm(list(range(8)), n_jobs=2)
    Parallel(n_jobs=2)(delayed(lambda i: time.sleep(2))(i) for i in x)
    x.finished()

    print('done')