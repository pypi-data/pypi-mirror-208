import argparse
import os
import warnings

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.io import mmwrite
from scipy.sparse import csr_matrix


def h5ad2mtx(adata: sc.AnnData, outdir, filed='integer'):
    """
    field: 'integer' or 'real'
    """
    if os.path.exists(outdir):
        print("Output directory already exists. Overwriting...")
    else:
        os.makedirs(outdir)
    adata.X = csr_matrix(adata.X)
    
    print("checking adata.X...")
    if filed == 'integer':
        if (adata.X - adata.X.astype(int)).nnz > 0:
            print("WARNING: adata.X contains non-integer values. Converting to integer...")
            adata.X = adata.X.astype(int)
    
    print("writing mtx files...")
    mmwrite(outdir + '/matrix.mtx', csr_matrix(adata.X), field=filed)
    adata.obs.to_csv(outdir + "/metadata.txt", sep='\t')
    pd.DataFrame(adata.var_names).to_csv(outdir + "/features.txt",
                                         sep='\t',
                                         header=None,
                                         index=0)
    print("Done.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_path', type=str, help='path to h5ad file')
    parser.add_argument('-o', '--output_dir', type=str, help='path to output directory')
    args = parser.parse_args()

    print("Reading h5ad file...")
    adata = sc.read_h5ad(args.input_path)
    outdir = args.output_dir

    print("Writing mtx files...")
    h5ad2mtx(adata, outdir)
