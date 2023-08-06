from typing import Callable

import scanpy as sc


def _base_integration(adata: sc.AnnData, method: Callable, key_added: str, **kwargs):
    """
    params:
    ---
    adata: AnnData
        input AnnData object
    method: Callable
        integration method
    key_added: str
        key to add to adata.obsm
    kwargs: dict
        keyword arguments to pass to `method`
    """
    integrated = method(adata, **kwargs)

    if sc.settings.verbosity > 1:
        print(f' -> adding `{key_added}` to `adata.obsm`')
    adata.obsm[key_added] = integrated

    return adata

