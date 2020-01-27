#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-visualize_local
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=24:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

source ~/venvs/gg/bin/activate

export TRD_CNT=8
export ST_TM=2019-12-01-00
export SP_TM=2020-01-01-00
export VIZ_CNT=3
export VIZ_D=3
export MD=S
python src/visualize_local.py
