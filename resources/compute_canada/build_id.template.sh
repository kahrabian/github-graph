#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-build_id
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=1:00:00
#SBATCH --array=0-35
#SBATCH --output=./logs/%x-%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

module load python/3

export TOTAL_THREADS=72
python src/build_id.py
