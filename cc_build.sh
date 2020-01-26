#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-build
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=2:00:00
#SBATCH --array=0-35
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca
#SBATCH --export=TOTAL_THREADS=36

source ~/venvs/gg/bin/activate
python build.py