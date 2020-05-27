#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-one-year
#SBATCH --cpus-per-task=20
#SBATCH --mem=350G
#SBATCH --time=1-0
#SBATCH --output=./logs/%x-%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

module load python/3.7.4

export TRD_CNT=20
python src/one_year.py
