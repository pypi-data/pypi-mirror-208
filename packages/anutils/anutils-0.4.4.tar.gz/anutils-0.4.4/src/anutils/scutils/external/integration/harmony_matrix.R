suppressPackageStartupMessages(library(harmony))
suppressPackageStartupMessages(library(argparse))

# Parse arguments
parser <- ArgumentParser()
parser$add_argument("-i", "--input_file", required = TRUE, help = "Input matrix file of tsv format")
parser$add_argument("-o", "--output_file", required = TRUE, help = "Output matrix file of tsv format")
parser$add_argument("--metadata_file", required = TRUE, help = "Metadata file of tsv format")
parser$add_argument("-b", "--batch_key", required = TRUE, help = "Batch key")
# harmony arguments
# HarmonyMatrix(
#   data_mat,
#   meta_data,
#   vars_use,
#   do_pca = TRUE,
#   npcs = 20,
#   theta = NULL,
#   lambda = NULL,
#   sigma = 0.1,
#   nclust = NULL,
#   tau = 0,
#   block.size = 0.05,
#   max.iter.harmony = 10,
#   max.iter.cluster = 200,
#   epsilon.cluster = 1e-05,
#   epsilon.harmony = 1e-04,
#   plot_convergence = FALSE,
#   return_object = FALSE,
#   verbose = TRUE,
#   reference_values = NULL,
#   cluster_prior = NULL
# )
parser$add_argument("--theta", type = "double", required = FALSE, default = NULL, help = "Theta")
parser$add_argument("--lambda", type = "double", required = FALSE, default = NULL, help = "Lambda")
parser$add_argument("--sigma", type = "double", required = FALSE, default = 0.1, help = "Sigma")
parser$add_argument("--tau", type = "double", required = FALSE, default = 0, help = "Tau")
parser$add_argument("--max_iter_harmony", type = "double", required = FALSE, default = 10, help = "Max iteration of harmony")
parser$add_argument("--max_iter_cluster", type = "double", required = FALSE, default = 200, help = "Max iteration of cluster")
parser$add_argument("--epsilon_cluster", type = "double", required = FALSE, default = 1e-05, help = "Epsilon of cluster")
parser$add_argument("--epsilon_harmony", type = "double", required = FALSE, default = 1e-04, help = "Epsilon of harmony")
args <- parser$parse_args()

# Read data
message('Reading data...')
data <- read.table(args$input_file, sep = '\t')
metadata <- read.table(args$metadata_file, sep = '\t', header = 1, row.names = 1)

cat('shape of adata: ', dim(data), '\n')
cat('there are ', length(unique(metadata[[args$batch_key]])), ' batches\n')

# Run Harmony
message('Running Harmony...')
data.harmony <- HarmonyMatrix(
    data, metadata, args$batch_key, do_pca = FALSE, 
    theta = args$theta, 
    lambda = args$lambda, 
    sigma = args$sigma, 
    tau = args$tau, 
    max.iter.harmony = args$max_iter_harmony, 
    max.iter.cluster = args$max_iter_cluster, 
    epsilon.cluster = args$epsilon_cluster, 
    epsilon.harmony = args$epsilon_harmony
)

# Write data
message('Writing data...')
cat('Writing data to ', args$output_file, '\n')
write.table(data.harmony, file = args$output_file, sep = '\t', row.names = FALSE, col.names = FALSE)

message('Done.')