import muon as mu
import numpy as np
import scanpy as sc
import scipy.sparse as sp
from matplotlib import pyplot as plt
from scipy import stats
from sklearn.preprocessing import MaxAbsScaler


def batch_scale(adata, batch_key='batch', chunk_size=20000):
    """
    Batch-specific scale data
    
    Parameters
    ----------
    adata
        AnnData
    chunk_size
        chunk large data into small chunks
    
    Return
    ------
    AnnData
    """
    adata.X = sp.csr_matrix(adata.X)
    assert (adata.X.data > 0).all(), 'Data must be positive for batch scale!'
    for b in adata.obs[batch_key].unique():
        idx = np.where(adata.obs[batch_key] == b)[0]
        scaler = MaxAbsScaler(copy=False).fit(adata.X[idx])
        for i in range(len(idx) // chunk_size + 1):
            adata.X[idx[i * chunk_size:(i + 1) * chunk_size]] = scaler.transform(
                adata.X[idx[i * chunk_size:(i + 1) * chunk_size]])

    return adata


def rna_preprocess(adata,
                   min_features=150,
                   min_cells=3,
                   pct_counts_mt=20,
                   target_sum=None,
                   log1p=True,
                   n_top_features=None,
                   remove_doublets=False,
                   transform=None,
                   inplace=True):
    """
    scRNA-seq data preprocess
    """
    if not inplace:
        adata = adata.copy()

    adata.layers['counts'] = adata.X
    sc.pp.filter_cells(adata, min_genes=min_features)
    sc.pp.filter_genes(adata, min_cells=min_cells)

    if pct_counts_mt is not None:
        adata.var['mt'] = adata.var_names.str.startswith(tuple(['ERCC', 'MT-', 'mt-']))
        sc.pp.calculate_qc_metrics(adata,
                                   qc_vars=['mt'],
                                   percent_top=None,
                                   log1p=False,
                                   inplace=True)
        mu.pp.filter_obs(adata, 'pct_counts_mt', lambda x: x < pct_counts_mt)

    if remove_doublets:
        sc.external.pp.scrublet(adata, verbose=sc.settings.verbosity > 1)

    sc.pp.normalize_total(adata, target_sum=target_sum)
    if log1p:
        sc.pp.log1p(adata)
    adata.raw = adata
    if n_top_features is not None:
        if type(n_top_features) == int:
            if n_top_features > 0:
                sc.pp.highly_variable_genes(adata, n_top_genes=n_top_features, subset=True)
            else:
                raise ValueError("Illegal n_top_features input!")
        elif type(n_top_features) == str:
            n_top_features = np.loadtxt(n_top_features, dtype=str)
            idx = [i for i, g in enumerate(n_top_features) if g in adata.var_names]
            adata = adata[:, idx]
    if transform:
        if sc.settings.verbosity > 1:
            print('transform...')
        transform(adata)

    return adata if not inplace else None


def atac_preprocess(adata,
                    min_features=200,
                    min_cells=3,
                    peaks_filter_ratio=0.75,
                    n_top_regions=None,
                    transform=None,
                    inplace=True):
    """
    scATAC-seq data preprocess, tf-idf normalization is used.
    """
    if not inplace:
        adata = adata.copy()

    adata.layers['counts'] = adata.X
    sc.pp.filter_cells(adata, min_genes=min_features)
    sc.pp.filter_genes(adata, min_cells=min_cells)
    mu.atac.pp.tfidf(adata, scale_factor=1e4)
    sc.pp.normalize_per_cell(adata, counts_per_cell_after=1e4)
    sc.pp.log1p(adata)
    if peaks_filter_ratio:
        quantile = adata.var.n_cells.quantile(peaks_filter_ratio)
        mu.pp.filter_var(adata, 'n_cells', lambda x: x > quantile)
    adata.raw = adata
    if n_top_regions is not None:
        sc.pp.highly_variable_genes(adata, n_top_genes=n_top_regions, subset=True)
    if transform:
        if sc.settings.verbosity > 1:
            print('transform...')
        transform(adata)

    return adata if not inplace else None


def qc_glance(ad, groupby=None, rotation=90):
    ad.var['mt'] = ad.var_names.str.startswith(tuple(
        ['ERCC', 'MT-', 'mt-']))  # annotate the group of mitochondrial genes as 'mt'
    sc.pp.calculate_qc_metrics(ad, qc_vars=['mt'], percent_top=None, log1p=True, inplace=True)
    sc.pl.violin(ad, ['total_counts', 'n_genes_by_counts', 'pct_counts_mt'],
                 groupby=groupby,
                 rotation=rotation)
    sc.pl.violin(ad, ['log1p_total_counts', 'log1p_n_genes_by_counts', 'log1p_total_counts_mt'],
                 groupby=groupby,
                 rotation=rotation)
    sc.pl.scatter(ad, x='total_counts', y='n_genes_by_counts', color='pct_counts_mt')


def qc_outliers(
    ad,
    groupby=None,
    rotation=90,
    nmads=5,
    qc_keys=['log1p_total_counts', 'log1p_n_genes_by_counts', 'log1p_total_counts_mt'],
):
    """identify outliers with values out of nmads * median absolute deviation (MAD) range
    
    add key `is_outlier` to `adata.obs` and plot violin plots with outliers highlighted

    Parameters
    ----------
    ad : AnnData
        adata
    groupby : str, optional
        identify outliers separately for each group, by default None
    rotation : int, optional
        rotate x tick labels to avoid overlapping, by default 90
    nmads : int, optional
        number of MADs to define outliers, by default 5
    qc_keys : list, optional
        qc values to define outliers on, by default ['log1p_total_counts', 'log1p_n_genes_by_counts', 'log1p_total_counts_mt']
    """

    def outlier_limits(x, nmads):
        median = np.median(x)
        mad = stats.median_abs_deviation(x)
        return median - nmads * mad, median + nmads * mad

    def get_limits_from_meta(df, qc_keys, nmads):
        limits = {}
        for key in qc_keys:
            limits[key] = outlier_limits(df[key].values, nmads)
        return limits

    # calculate limits and outliers
    limits = {}
    is_outlier = np.zeros(ad.n_obs, dtype=bool)
    meta = ad.obs.copy()
    if groupby is None:
        limits['__all'] = get_limits_from_meta(meta, qc_keys, nmads)
    else:
        for group in sorted(meta[groupby].unique().tolist()):
            limits[group] = get_limits_from_meta(meta[meta[groupby] == group], qc_keys, nmads)
            for qc_key in qc_keys:
                is_outlier = is_outlier | ((meta[groupby] == group).values
                                           & ((meta[qc_key] < limits[group][qc_key][0]).values
                                              |
                                              (meta[qc_key] > limits[group][qc_key][1])).values)
    ad.obs['is_outlier'] = is_outlier
    if sc.settings.verbosity > 1:
        print(f'{sum(is_outlier)} outliers out of {ad.n_obs} cells')
        print(f'Outlier rate: {sum(is_outlier) / ad.n_obs:.2%}')
        print(f' -> added key `is_outlier` to `adata.obs`')

    axes = sc.pl.violin(ad, qc_keys, groupby=groupby, rotation=rotation, show=False)
    fig = axes[0].figure
    if len(axes) == 1:
        axes = [axes]
    for ax, qc_key in zip(axes, qc_keys):
        xticks = ax.get_xticks()
        xticklabels = ax.get_xticklabels()
        xsep = xticks[1] - xticks[0]
        patch_width = xsep * .9
        for x, label, (group, lims) in zip(xticks, xticklabels, limits.items()):
            if group != '__all':
                assert group == label.get_text()
            # draw patch
            ax.add_patch(
                plt.Rectangle((x - patch_width / 2, lims[qc_key][0]),
                              patch_width,
                              lims[qc_key][1] - lims[qc_key][0],
                              fill=True,
                              edgecolor=None,
                              facecolor='g',
                              alpha=0.2,
                              lw=0))

    fig.show()