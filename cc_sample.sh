#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-sample
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=2:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca
#SBATCH --export=TRD_CNT=16
#SBATCH --export=ST_TM=2019-12-01-00
#SBATCH --export=SP_TM=2020-01-01-00
#SBATCH --export=IN_SZ=2000
#SBATCH --export=TG_SZ=2000000
#SBATCH --export=SMPL_RT=2000

source ~/venvs/gg/bin/activate
python sample.py
