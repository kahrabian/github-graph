#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-visualize_local
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=2:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

source ~/venvs/gg/bin/activate

export TRD_CNT=16
export ST_TM=2019-12-01-00
export SP_TM=2020-01-01-00
export VIZ_CNT=10
export VIZ_D=5
export MD=S
python src/visualize_local.py
