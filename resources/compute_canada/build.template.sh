#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-build
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=1:00:00
#SBATCH --array=0-35
#SBATCH --output=./logs/%x-%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

source activate gg

export TOTAL_THREADS=36
python src/build.py
