# anutils
ML and single cell analysis utils.  

## installation
```
pip install anutils
```
**NOTE**: To use `anutils.scutils.sc_cuda`, you need to install rapids first. see [rapids.ai](https://rapids.ai/start.html) for details. For example, to install rapids on a linux machine with cuda 11, you can run:  
```bash
pip install cudf-cu11 dask-cudf-cu11 --extra-index-url=https://pypi.nvidia.com
pip install cuml-cu11 --extra-index-url=https://pypi.nvidia.com
pip install cugraph-cu11 --extra-index-url=https://pypi.nvidia.com
```

## usage

### general utils: `anutils.*`

`anutls.glimpse` is similar to `dplyr::glimpse` in R, but enhanced in:
- display the index
- when passing `show_unique=True`, display the number of unique values for each column
- when passing `show_unique=True`, display the unique values instead of the first N values for each column

```python
import anutils as anu

df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Carol', 'David', 'Eric'],
    'letters': ['a', 'a', 'b', 'b', 'c'],
    'digits': [1, 2, 3, 3, 3],
    'colors': ['r', 'g', 'b', 'k', 'k'],
})
df.index = df['name']
anu.glimpse(df, show_unique=True)

# output:
# DataFrame: 5 rows, 4 columns
# index (name)   <object> (5) ['Alice', 'Bob', 'Carol', 'David', 'Eric']
# $ name         <object> (5) ['Alice', 'Bob', 'Carol', 'David', 'Eric']
# $ letters      <object> (3) ['a', 'b', 'c']
# $ digits       <int64>  (3) [1, 2, 3]
# $ colors       <object> (4) ['r', 'g', 'b', 'k']
```


### single cell utils: `anutils.scutils.*`

#### plotting

```python
from anutils import scutils as scu

# a series of embeddings grouped by disease status
scu.pl.embeddings(adata, basis='X_umap', groupby='disease_status', **kwargs) # kwargs for sc.pl.embedding

# enhanced dotplot with groups in hierarchical order
scu.pl.dotplot(adata, var_names, groupby, **kwargs) # kwargs for sc.pl.dotplot
```
#### cuda-accelerated scanpy functions
NOTE: to use these functions, you need to install rapids first. see [installation](#installation) for details.
```python
from anutils.scutils import sc_cuda as cusc

# 10-100 times faster than `scanpy.tl.leiden`
cusc.sc.leiden(adata, resolution=0.5, key_added='leiden_0.5')

# 10-100 times faster than `scib.metrics.silhouette`
cusc.sb.silhouette(adata, group_key, embed)
```

## machine learning utils:
```python
import anutils.mlutils as ml

# to be added
```
