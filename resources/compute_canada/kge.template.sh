#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-kge
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:t4:4
#SBATCH --cpus-per-task=16
#SBATCH --mem=196608M
#SBATCH --time=24:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

source activate gg

graphvite run ./resources/graphvite/kg_simple.yaml
