def filter_batches_with_too_few_samples(adata,
                                        batch_key,
                                        min_samples,
                                        inplace=True,
                                        copy=False,
                                        verbose=True
                                        ):
    """
    params:
    ---
    adata: AnnData
        AnnData object
    batch_key: str
        key in `adata.obs` to use for batch
    min_samples: int
        minimum number of samples in a batch to keep
    
    returns:
    ---
    adata: anndata.AnnData
        AnnData object with batches with fewer than `min_samples` removed
    """
    batch_sizes = adata.obs[batch_key].value_counts()
    batches_to_keep = batch_sizes[batch_sizes >= min_samples].index
    if verbose:
        # show name and n_obs of batches with too few samples
        print(f'Filtering batches with fewer than {min_samples} samples:')
        print(batch_sizes[batch_sizes < min_samples])
    if inplace:
        adata._inplace_subset_obs(adata.obs[batch_key].isin(batches_to_keep))
    else:
        adata = adata[adata.obs[batch_key].isin(batches_to_keep)]
    return adata if copy else None
