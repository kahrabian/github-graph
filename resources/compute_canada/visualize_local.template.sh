#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-visualize_local
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=1-0
#SBATCH --output=./logs/%x-%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

source activate gg

export TRD_CNT=8
export MD=S
export ST_TM=2019-12-01-00
export SP_TM=2020-01-01-00
export VIZ_CNT=2
export VIZ_D=2
python src/visualize_local.py
