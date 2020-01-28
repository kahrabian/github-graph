#!/bin/bash
#SBATCH --account=def-jinguo
#SBATCH --job-name=gg-kge
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=10
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kian.ahrabian@mail.mcgill.ca

source activate gg

graphvite run ./resources/graphvite/kg_simple.yaml
