#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-split
#SBATCH --cpus-per-task=4
#SBATCH --mem=1G
#SBATCH --time=3:00:00
#SBATCH --output=./logs/%x-%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

source activate gg

export TRD_CNT=8
export MD=S
export TS_MD=H
export TPS=U_SE_C_I
export TR_TM=2019-12-01-00
export VD_TM=2019-12-26-00
export TS_TM=2019-12-29-00
export ST_TM=2020-01-01-00
python src/split_time.py
