#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-one-year-nodes
#SBATCH --cpus-per-task=1
#SBATCH --mem=128G
#SBATCH --time=1-0
#SBATCH --array=0-15
#SBATCH --output=./logs/%x-%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

module load python/3

export TRD_CNT=2
export TOTAL_JOBS=16
python src/one_year_nodes.py
