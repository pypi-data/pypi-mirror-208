import os

import pandas as pd
import scanpy as sc
import scipy.io

from anutils.scutils.data.h5ad2mtx import h5ad2mtx

# def ad2mtx(ad_path: str) -> None:
#     r"""
#     convert adata to: `matrix.mtx`, `genes.txt` and `metadata.txt`
#     """
#     adata = sc.read_h5ad(ad_path)
#     outdir = os.path.dirname(ad_path)
#     scipy.io.mmwrite(os.path.join(outdir, 'matrix.mtx'), adata.X, field='integer')
#     adata.obs.to_csv(os.path.join(outdir, "metadata.txt"), sep='\t')
#     pd.DataFrame(adata.var_names).to_csv(os.path.join(outdir, "genes.txt"),
#                                          sep='\t',
#                                          header=None,
#                                          index=0)


def read_10X_multi(matrix_dir: str):
    r"""
    matrix_dir: downloaded from 10x website, containing matrix.mtx.gz, barcodes.tsv.gz and features.tsv.gz
    """
    mat_path = os.path.join(matrix_dir, "matrix.mtx.gz")
    mat = scipy.io.mmread(mat_path)

    features_path = os.path.join(matrix_dir, "features.tsv.gz")
    features = pd.read_table(features_path, header=None)
    features.columns = [
        'feature_id', 'feature_name', 'feature_type', 'chrom', 'chromStart', 'chromEnd'
    ]
    features.index = features.feature_id.values
    features = features.drop('feature_id', axis=1)

    barcodes_path = os.path.join(matrix_dir, "barcodes.tsv.gz")
    barcodes = pd.read_table(barcodes_path, header=None)
    barcodes.columns = ['barcode']
    barcodes.index = barcodes.barcode.values
    barcodes = barcodes.drop('barcode', axis=1)

    adata = sc.AnnData(X=mat.tocsr().transpose(), obs=barcodes, var=features)
    adata.obs.index = adata.obs.index.str[:-2]

    ad_r, ad_a = adata[:, adata.var.feature_type ==
                       'Gene Expression'], adata[:, adata.var.feature_type == 'Peaks']

    ad_r.var = ad_r.var.rename(columns={
        'feature_name': 'gene_name'
    }).drop('feature_type', axis=1)
    ad_a.var = ad_a.var.rename(columns={'feature_name': 'peak'}).drop('feature_type', axis=1)

    try:
        ad = ad_r.copy()
        add_gene_anno(ad)
        ad_r = ad
    except Exception as e:
        print(e)
        print('failed add annos. return original. ')

    ad_r.var = convert_dtype(ad_r.var)
    ad_r.obs = convert_dtype(ad_r.obs)
    ad_a.var = convert_dtype(ad_a.var)
    ad_a.obs = convert_dtype(ad_a.obs)

    return ad_r, ad_a


def convert_dtype(df: pd.DataFrame,
                  from_dtype: str = 'object',
                  to_dtype: str = 'str') -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == from_dtype:
            df[col] = df[col].astype(to_dtype)
    if df.index.dtype == from_dtype:
        df.index = df.index.astype(to_dtype)
    return df


def add_gene_anno(adata: sc.AnnData,
                  anno_file: str = None,
                  filter_MT: bool = True) -> sc.AnnData:
    r"""add gene annotations
    
    from `/home/ningweixi/projects/MISC/PairedDataset.py`
    """
    if anno_file is None:
        anno_file = '/data1/ningweixi/tiankang/resources/gene_info_human.txt'

    gene_info = pd.read_csv(anno_file, sep='\t').astype(str)
    gene_info.chromStart = gene_info.chromStart.astype(int)
    gene_info.chromEnd = gene_info.chromEnd.astype(int)

    gene_info.drop_duplicates(subset=['name'], inplace=True)
    gene_info.index = gene_info['gene_id']
    adata.var = adata.var.astype(str)
    adata.var = pd.concat([adata.var, gene_info], axis=1).reindex(adata.var_names).fillna(0)
    adata.var.chromStart = adata.var.chromStart.astype(int)
    adata.var.chromEnd = adata.var.chromEnd.astype(int)

    adata.var = adata.var.loc[:, ~adata.var.columns.duplicated()]

    if filter_MT:
        adata = adata[:, adata.var.chrom != 0]

    return adata


def make_gene_symbols_unique(adata: sc.AnnData) -> sc.AnnData:
    # TODO
    pass


def get_ncells_from_h5ad(h5ad_path: str) -> int:
    return len(sc.read(h5ad_path).obs)
