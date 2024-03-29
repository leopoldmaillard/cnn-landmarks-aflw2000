#!/bin/bash

# Created from: slurm submission script, serial job
# support@criann.fr

# Max time the script will run (here 3 hours)
#SBATCH --time 03:00:00

# RAM to use (Mo)
#SBATCH --mem 50000

# Number of cpu core to use
#SBATCH --cpus-per-task=10

# Enable the mailing for the start of the experiments
#SBATCH --mail-type ALL
#SBATCH --mail-user leopold.maillard@insa-rouen.fr

# Which partition to use
#SBATCH --partition insa

# Number of gpu(s) to use
#SBATCH --gres gpu:1

# Number of nodes to use
#SBATCH --nodes 1

# Log files (%J is a variable for the job id)
#SBATCH --output %J.out
#SBATCH --error %J.err

#Loading the module
module load python3-DL/3.8.5

# Creating a directory to save the training weights
# mkdir callbacks

# Define the repository where the trained weights will be stored
# This variable is used in the script
# export LOCAL_WORK_DIR=checkpoints

# Start the calculation
srun python3 test_heatmap_lucie.py
