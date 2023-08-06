suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(Seurat))
suppressPackageStartupMessages(library(scater))
suppressPackageStartupMessages(library(future))
suppressPackageStartupMessages(library(Matrix))
suppressPackageStartupMessages(library(future.apply))

parser <- ArgumentParser(description='Seurat_v3 for the integrative analysis of multi-batch single-cell transcriptomic profiles')
parser$add_argument("-i", "--input_path", type="character", help="Path contains RNA data")
parser$add_argument("-o", "--output_path", type="character", default='/home/tiankang/SCALEX/results/Seurat_v3', help="Output path")
parser$add_argument("-mf", "--minFeatures", type="integer", default=600, help="Remove cells with less than minFeatures features")
parser$add_argument("-mc", "--minCells", type="integer", default=3, help="Remove features with less than minCells cells")
parser$add_argument("-nt", "--n_top_features", type="integer", default=2000, help="N highly variable features")
parser$add_argument("-nj", "--n_jobs", type="integer", default=1, help="Number of jobs")
parser$add_argument("--batch_key", type="character", default='batch', help="Batch key")
parser$add_argument("--k_anchor", type="integer", default=5, help="k.anchor")
parser$add_argument("--k_filter", type="integer", default=200, help="k.filter")
parser$add_argument("--k_score", type="integer", default=30, help="k.score")
args <- parser$parse_args()

plan("multiprocess", workers = args$n_jobs)
options(future.globals.maxSize = 100000 * 1024^2, warn = -1)

# Read data
message('Reading data...')
data <- readMM(paste(args$input_path, '/matrix.mtx', sep=''))
genes <- read.table(paste(args$input_path, '/features.txt', sep=''), sep='\t')
metadata <- read.csv(paste(args$input_path, '/metadata.txt', sep=''), sep='\t')
row.names(metadata) <- metadata[,1]
metadata <- metadata[,-1]
metadata[[args$batch_key]] = as.character(metadata[[args$batch_key]])
data <- t(data)
colnames(data) <- row.names(metadata) 
row.names(data) <- genes[,1]

message('CreateSeuratObject...')
adata <- CreateSeuratObject(as(data, "sparseMatrix"), 
                           meta.data = metadata,
                           min.cells = args$minCells, 
                           min.features = args$minFeatures)

cat('shape of adata: ', dim(adata), '\n')
cat('there are ', length(unique(metadata[[args$batch_key]])), ' batches\n')

# PP and integration
adata.list <- SplitObject(adata, split.by = args$batch_key)

message('Preprocessing each batch...')
adata.list <- future_lapply(X = adata.list, FUN = function(x) {
    # calculate percent.mito
    # x <- PercentageFeatureSet(x, pattern = "^MT-", col.name = "percent.mito")
    x <- NormalizeData(x, verbose = FALSE)
    x <- FindVariableFeatures(x, nfeatures = args$n_top_features, selection.method = "vst", verbose = FALSE)
    # x <- ScaleData(x, verbose = FALSE, vars.to.regress = c('nUMI', 'percent.mito'))
}, future.seed = TRUE)

message('SelectIntegrationFeatures...')
features <- SelectIntegrationFeatures(object.list = adata.list)

message('PCA each batch...')
adata.list <- future_lapply(X = adata.list, FUN = function(x) {
    x <- ScaleData(x, features = features, verbose = FALSE)
    x <- RunPCA(x, features = features, verbose = FALSE)
}, future.seed = TRUE)

message('FindIntegrationAnchors...')
adata.anchors <- FindIntegrationAnchors(object.list = adata.list, dims = 1:30, verbose = FALSE, reduction = 'rpca')

message('IntegrateData...')
adata.integrated <- IntegrateData(anchorset = adata.anchors, dims = 1:30, verbose = FALSE)

message('RunPCA...')
adata.integrated <- ScaleData(adata.integrated, verbose = FALSE)
adata.integrated <- RunPCA(adata.integrated, npcs = 50, verbose = FALSE)

# write outputs
if (!file.exists(args$output_path)){
    dir.create(file.path(args$output_path),recursive = TRUE)
}
message('Writing outputs...')
cat('Writing pcs to ', args$output_path, '/pcs.txt\n', sep='')
cat('Writing meta to ', args$output_path, '/meta.txt\n', sep = '')
write.table(adata.integrated@meta.data[,-1:-3], paste0(args$output_path, '/meta.txt'), sep = '\t')
write.table(adata.integrated@reductions$pca@cell.embeddings, paste0(args$output_path, '/pcs.txt'), sep = '\t')

message('Done!')