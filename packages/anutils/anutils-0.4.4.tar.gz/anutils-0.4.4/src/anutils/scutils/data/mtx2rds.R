suppressPackageStartupMessages(library(argparse))
suppressPackageStartupMessages(library(Seurat))
suppressPackageStartupMessages(library(Matrix))

parser$add_argument("-i", "--input_dir", type="character", help="dir with matrix.mtx")
parser$add_argument("-o", "--output_path", type="character", help="output path of the rds file")

if (!endsWith(args$output_path, '.rds')) {
    warning('output_path does not end with .rds, adding it...')
  args$output_path <- paste0(args$output_path, '.rds')
}

message('Reading...')
data <- readMM(paste(args$input_dir, '/matrix.mtx', sep=''))
genes <- read.table(paste(args$input_dir, '/features.txt', sep=''), sep='\t')
metadata <- read.csv(paste(args$input_dir, '/metadata.txt', sep=''), sep='\t')
row.names(metadata) <- metadata[,1]
metadata <- metadata[,-1]

data <- t(data)

colnames(data) <- row.names(metadata) 
row.names(data) <- genes[,1]

message('CreateSeuratObject...')
adata <- CreateSeuratObject(as(data, "sparseMatrix"), 
                           meta.data = metadata,
                           min.cells = args$minCells, 
                           min.features = args$minFeatures)

message('saveRDS...')
saveRDS(adata, args$output_path)

message('done.')