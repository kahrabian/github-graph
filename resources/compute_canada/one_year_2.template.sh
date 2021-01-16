#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-one-year-2
#SBATCH --cpus-per-task=8
#SBATCH --mem=100G
#SBATCH --time=3:00:00
#SBATCH --output=./logs/%x-%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

module load python/3

export TRD_CNT=16
python src/one_year_2.py
