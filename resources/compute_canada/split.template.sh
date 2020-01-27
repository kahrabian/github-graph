#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-split
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=1:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

source ~/venvs/gg/bin/activate

export TRD_CNT=8
export MD=S
export ST_TM=2019-12-01-00
export TR_TM=2019-12-22-00
export VD_TM=2019-12-27-00
export SP_TM=2020-01-01-00
python src/split.py
