#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-one-year
#SBATCH --cpus-per-task=16
#SBATCH --mem=350G
#SBATCH --time=12:00:00
#SBATCH --output=./logs/%x-%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

module load python/3

export TRD_CNT=32
python src/one_year.py
