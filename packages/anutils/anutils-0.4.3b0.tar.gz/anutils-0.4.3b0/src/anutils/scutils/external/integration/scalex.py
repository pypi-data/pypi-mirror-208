def scalex(
    adata,
    batch,
    output_path=None,
    return_model=False,
    seed=0,
    lr=1e-3,
    max_iteration=30000,
    batch_size=64,
    hidden_dim=1024,
    latent_dim=10,
    verbose=False,
    batch_scale=True,
    key_added='X_scalex',
):
    """
    NOTE: it is assumed that the data in `adata.X` is already log transformed and normalized.
    NOTE: SCALEX use scales each batch to [0, 1] range. If it is already scaled, set `batch_scale=False`.
    NOTE: the scaling is not done in-place, so the original data is not modified.
    NOTE: the latent representation is saved to `adata.obsm[key_added]`, inplace.
    
    batch: batch key
    """
    import os

    import numpy as np
    import torch
    from scalex.data import BatchSampler, SingleCellDataset
    from scalex.logger import create_logger
    from scalex.net.utils import EarlyStopping
    from scalex.net.vae import VAE
    from torch.utils.data import DataLoader

    from anutils.scutils.preprocessing import batch_scale as batch_scale_fn

    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        device = 'cuda'
    else:
        device = 'cpu'

    if output_path:
        os.makedirs(output_path + '/checkpoint', exist_ok=True)
        log = create_logger('SCALEX', fh=output_path + '/log.txt', overwrite=True)
    else:
        log = create_logger('SCALEX')

    # prepare data
    adata_new = adata.copy()
    # scale data to [0, 1] range
    if batch_scale:
        log.info('Batch specific maxabs scaling')
        adata_new = batch_scale_fn(adata_new, batch_key=batch)

    # prepare dataloader
    scdata = SingleCellDataset(adata_new)  # Wrap AnnData into Pytorch Dataset
    trainloader = DataLoader(scdata,
                             batch_size=batch_size,
                             drop_last=True,
                             shuffle=True,
                             num_workers=4)
    batch_sampler = BatchSampler(batch_size, adata_new.obs['batch'], drop_last=False)
    testloader = DataLoader(scdata, batch_sampler=batch_sampler)

    early_stopping = EarlyStopping(patience=10,
                                   checkpoint_file=output_path +
                                   '/checkpoint/model.pt' if output_path else None)

    # model config
    x_dim, n_domain = adata_new.shape[1], len(adata_new.obs[batch].cat.categories)
    enc = [['fc', hidden_dim, 1, 'relu'], ['fc', latent_dim, '', '']]
    dec = [['fc', x_dim, n_domain, 'sigmoid']]

    model = VAE(enc, dec, n_domain=n_domain)

    # train
    model.fit(
        trainloader,
        lr=lr,
        max_iteration=max_iteration,
        device=device,
        early_stopping=early_stopping,
        verbose=verbose,
    )
    if output_path:
        torch.save(
            {
                'n_top_features': adata_new.var.index,
                'enc': enc,
                'dec': dec,
                'n_domain': n_domain
            }, output_path + '/checkpoint/config.pt')

    # save latent rep to adata
    # del adata_new
    log.info(f'saving latent representation to adata.obsm[{key_added}]')
    adata.obsm[key_added] = model.encodeBatch(testloader, device=device, eval=eval)

    model.to('cpu')
    if not return_model:
        del model

    if output_path is not None:
        adata.write(output_path + '/adata.h5ad', compression='gzip')

    return model if return_model else adata