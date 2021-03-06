#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-split
#SBATCH --cpus-per-task=4
#SBATCH --mem=1G
#SBATCH --time=3:00:00
#SBATCH --output=./logs/%x-%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

module load python/3

export TRD_CNT=4
export DIR=sample
export TPS=U_SE_C_I,U_SO_C_P
export SP=I
python src/split.py
