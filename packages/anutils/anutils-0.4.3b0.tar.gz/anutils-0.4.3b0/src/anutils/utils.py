r"""
A.N. 202206
---
general utils.
"""
import datetime
import logging
import os
import sys
import time
import warnings
from importlib import reload
from types import ModuleType

from getkey import getkey


def rreload(module, max_depth, verbose=False, depth=0):
    """Recursively reload modules.
    
    NOTE: IPython.lib.deepreload.reload() is similar.
    """
    for attribute_name in dir(module):
        if not hasattr(module, attribute_name):
            continue
        attribute = getattr(module, attribute_name)
        if type(attribute) is ModuleType:
            if depth < max_depth:
                rreload(attribute, max_depth, verbose=verbose, depth=depth + 1)
    try:
        reload(module)
    except Exception as e:
        if verbose:
            print(f'Skip reloading `{module}`: {e}')
        pass


def flatten(lst: list) -> list:
    r"""
    flattens a list of lists or tuples.
    """
    ret = []
    for item in lst:
        if isinstance(item, (list, tuple)):
            ret += flatten(item)
        else:
            ret.append(item)
    return ret


def get_user_choice(prompt: str = 'please confirm', choices: list = None) -> str:
    r"""
    get **one** character from input
    """
    if choices is None:
        choices = ['y', 'n']
    while True:
        if not (prompt.endswith(':') or prompt.endswith(': ')):
            prompt += ':'
        print(f'{prompt} -> [{"/".join(choices)}] ', end='')
        sys.stdout.flush()
        key = getkey()
        print(key, end='')
        if key in choices:
            print()
            break
        else:
            print(' invalid input. ')
            continue
    return key


def print_with_time(*args, **kwargs):
    r"""print with time.
    """
    print(f'[{str(datetime.datetime.now())}]', end=' ')
    print(*args, **kwargs)
    sys.stdout.flush()


def silent(mode='all'):
    r"""silent a function.
    params:
        mode: 'all', 'err', 'warn' or 'out'
    """

    def silencer(fn):

        def wrapped(*args, **kwargs):
            oo, oe = sys.stdout, sys.stderr
            with open(os.devnull, 'w', encoding='utf-8') as devnull:
                if mode == 'out':
                    sys.stdout = devnull
                    ret = fn(*args, **kwargs)
                    sys.stdout = oo
                elif mode == 'err':
                    sys.stderr = devnull
                    ret = fn(*args, **kwargs)
                    sys.stderr = oo
                elif mode == 'all':
                    sys.stdout = devnull
                    sys.stderr = devnull
                    ret = fn(*args, **kwargs)
                    sys.stdout, sys.stderr = oo, oe
                elif mode == 'warn':
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore')
                        ret = fn(*args, **kwargs)
                else:
                    raise (ValueError("mode should be in ['out', 'err', 'all', 'warn']"))
            return ret

        return wrapped

    return silencer


class Silent():

    def __init__(self, mode):
        if isinstance(mode, str):
            mode = [mode]
        for item in mode:
            assert item in ['stdout', 'stderr']
        self.mode = mode
        self.out_bak = sys.stdout
        self.err_bak = sys.stderr
        self.devnull = open(os.devnull, 'w', encoding='utf-8')

    def __enter__(self):
        for mode in self.mode:
            if mode == 'stdout':
                sys.stdout = self.devnull
            elif mode == 'stderr':
                sys.stderr = self.devnull

    def __exit__(self, type, value, traceback):
        for mode in self.mode:
            if mode == 'stdout':
                sys.stdout = self.out_bak
            elif mode == 'stderr':
                sys.stderr = self.err_bak
        self.devnull.close()


def timing(fn, show_datetime: bool = True):
    r"""time a function.
    """

    def timed(*args, **kwargs):
        start = time.time()
        ret = fn(*args, **kwargs)
        tmstr = "{} elapse: {:.3f} s".format(fn.__name__, time.time() - start)
        if show_datetime:
            tmstr = ' '.join(['[' + str(datetime.datetime.now()) + ']', tmstr])
        print(tmstr)
        return ret

    return timed


def logging_to(target_dir: str, need_timing_in_name: bool = False):
    r"""log a function to a file.
    """
    assert os.path.isdir(target_dir)

    def decorator(fn):

        def logged_fn(*args, **kwargs):
            if need_timing_in_name:
                dt = datetime.datetime.now()
                txt_path = os.path.join(
                    target_dir,
                    "log_{:d}_{:d}_{:d}_{:d}_{:d}_{:d}.txt".format(dt.year, dt.month, dt.day,
                                                                   dt.hour, dt.minute,
                                                                   dt.second))
            else:
                txt_path = os.path.join(target_dir, 'log.txt')

            with open(txt_path, 'w', encoding='utf-8') as f:
                old_stdout = sys.stdout
                sys.stdout = f
                ret = fn(*args, **kwargs)
                sys.stdout = old_stdout
            return ret

        return logged_fn

    return decorator


def get_datetime_str() -> str:
    r"""get datetime str.
    """
    dt = datetime.datetime.now()
    dt_str = "{:d}_{:d}_{:d}_{:d}_{:d}_{:d}".format(dt.year, dt.month, dt.day, dt.hour,
                                                    dt.minute, dt.second)
    return dt_str


def create_logger(name='', ch=True, fh=None, levelname=logging.INFO, overwrite=False):
    # Author: Xiong Lei
    logger = logging.getLogger(name)
    logger.setLevel(levelname)

    if overwrite:
        for h in logger.handlers:
            logger.removeHandler(h)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler
    if ch:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    if fh is not None:
        fh = logging.FileHandler(fh, mode='w')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger


class Tee(object):
    """Tees stdout or stderr to a file.
    
    Parameters
    ---
    source: str
        'o' for stdout, 'e' for stderr
    name: str
        file name
    mode: str
        file mode, 'w' or 'a' etc.

    Examples
    ---
    tee stdout to a file:
    >>> tee = Tee('o', 'stdout.log', 'w')
    
    end the tee:
    >>> tee.__del__()
    
    https://stackoverflow.com/questions/616645/how-to-duplicate-sys-stdout-to-a-log-file/616686#616686
    """

    def __init__(self, source, name, mode):
        assert source in ['o', 'e']
        self.source = source
        self.file = open(name, mode)
        if 'o' in source:
            self.stdout = sys.stdout
            sys.stdout = self
        elif 'e' in source:
            self.stderr = sys.stderr
            sys.stderr = self

    def __del__(self):
        self.flush()
        if 'o' in self.source:
            sys.stdout = self.stdout
        elif 'e' in self.source:
            sys.stderr = self.stderr
        self.file.close()

    def write(self, data):
        self.file.write(data)
        if 'o' in self.source:
            self.stdout.write(data)
        elif 'e' in self.source:
            self.stderr.write(data)

    def flush(self):
        self.file.flush()
        if 'o' in self.source:
            self.stdout.flush()
        elif 'e' in self.source:
            self.stderr.flush()


def glimpse(df, n=5, show_unique=True, columns=None, truncate_at=100):
    """similar to R's `dplyr::glimpse`
    
    n: number of rows to show
    show_unique: show unique values
    columns: list of columns to show
    truncate_at: truncate string at
    """
    print(f"DataFrame: {df.shape[0]} rows, {df.shape[1]} columns")

    # info is a list of tuples
    # if `show_unique`, each tuple is (column_name, dtype, values, nunique)
    # else, each tuple is (column_name, dtype, values)
    info = []

    # index
    index_name = 'index ({})'.format(str(df.index.name) if df.index.name is not None else '')
    if show_unique:
        values = df.index.unique().tolist()[:n]
        nunique = df.index.nunique()
        info.append((index_name, str(df.index.dtype), values, nunique))
    else:
        values = df.index.head(n).values.tolist()
        info.append((index_name, str(df.index.dtype), values))

    # columns
    if columns is None:
        columns = df.columns
    for col in columns:
        if col not in df.columns:
            info.append((col, 'missing', [], 0))
        else:
            if show_unique:
                values = df[col].unique().tolist()[:n]
                nunique = df[col].nunique()
                info.append((col, str(df[col].dtype), values, nunique))
            else:
                values = df[col].head(n).values.tolist()
                info.append((col, str(df[col].dtype), values))

    max_len_col = max([len(i[0]) for i in info])
    max_len_dtype = max([len(i[1]) for i in info])
    if show_unique:
        max_len_unique = max([len(str(i[3])) for i in info])
    for irow, i in enumerate(info):
        # index
        if irow == 0:
            s = f"{i[0]:<{max_len_col+2}} {'<'+i[1]+'>':<{max_len_dtype+2}}"
        else:
            s = f"$ {i[0]:<{max_len_col}} {'<'+i[1]+'>':<{max_len_dtype+2}}"
        if show_unique:
            s += f" {'('+str(i[3])+')':<{max_len_unique+2}}"
        list_s = f"{i[2]}"
        if show_unique and i[3] <= n and len(list_s) <= truncate_at:
            pass
        else:
            list_s = list_s[:-1][:truncate_at] + ' ...'
        s += ' ' + list_s
        print(s)
    print()


def roman(num: int) -> str:

    chlist = "VXLCDM"
    rev = [int(ch) for ch in reversed(str(num))]
    chlist = ["I"] + [
        chlist[i % len(chlist)] + "\u0304" * (i // len(chlist)) for i in range(0,
                                                                               len(rev) * 2)
    ]

    def period(p: int, ten: str, five: str, one: str) -> str:
        if p == 9:
            return one + ten
        elif p >= 5:
            return five + one * (p - 5)
        elif p == 4:
            return one + five
        else:
            return one * p

    return "".join(
        reversed([
            period(rev[i], chlist[i * 2 + 2], chlist[i * 2 + 1], chlist[i * 2])
            for i in range(0, len(rev))
        ]))
