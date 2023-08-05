import os
import os.path as osp

import pandas as pd


def scvi(
    adata,
    batch,
    output_path=None,
    n_latent=30,
    n_hidden=128,
    n_layers=2,
    hvg=None,
    return_model=False,
    max_epochs=None,
    key_added=None,
):
    """scVI wrapper function
    
    from package `scib`. 

    Based on scvi-tools version >=0.16.0 (available through `conda <https://docs.scvi-tools.org/en/stable/installation.html>`_)

    .. note::
        scVI expects only non-normalized (count) data on highly variable genes!

    :param adata: preprocessed ``anndata`` object
    :param batch: batch key in ``adata.obs``
    :param hvg: list of highly variables to subset to. If ``None``, the full dataset will be used
    :return: ``anndata`` object containing the corrected feature matrix as well as an embedding representation of the
        corrected data
    """

    from scvi.model import SCVI

    if key_added is None:
        key_added = 'X_scvi'

    # Check for counts data layer
    if "counts" not in adata.layers:
        raise TypeError("Adata does not contain a `counts` layer in `adata.layers[`counts`]`")

    # Defaults from SCVI github tutorials scanpy_pbmc3k and harmonization
    # n_latent = 30
    # n_hidden = 128
    # n_layers = 2

    # copying to not return values added to adata during setup_anndata
    net_adata = adata.copy()
    if hvg is not None:
        net_adata = adata[:, hvg].copy()
    SCVI.setup_anndata(net_adata, layer="counts", batch_key=batch)

    vae = SCVI(
        net_adata,
        gene_likelihood="nb",
        n_layers=n_layers,
        n_latent=n_latent,
        n_hidden=n_hidden,
    )
    vae.train(train_size=1.0, max_epochs=max_epochs)

    latent = vae.get_latent_representation()
    adata.obsm[key_added] = latent

    # write latent to output_path
    if output_path is not None:
        latent = pd.DataFrame(latent, index=adata.obs_names)
        outdir = osp.dirname(output_path)
        if not osp.exists(outdir):
            os.makedirs(outdir)
        print(f'writing latent to {output_path}')
        latent.to_csv(output_path, sep='\t')

    if not return_model:
        return adata
    else:
        return vae