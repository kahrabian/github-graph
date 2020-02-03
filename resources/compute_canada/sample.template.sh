#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-sample
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=30:00
#SBATCH --output=./logs/%x-%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

source activate gg

export TRD_CNT=16
export ST_TM=2019-12-01-00
export SP_TM=2020-01-01-00
export IN_SZ=100
export TG_SZ=1000000
export SMPL_RT=100
python src/sample.py
