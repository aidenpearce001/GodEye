# About the project
GodEye

# Getting Started

## Prerequisites
- Download pre-trained model : [Pre-trained Model](https://drive.google.com/file/d/1VTy82gLD43JcTOVRHMrdXtXi3KSystH-/view?usp=sharing)
    `
    mv epoch.014-val_loss.18.4833.ckpt models/base_M/
    `

## Installation
- Setup env using conda

    `
    conda env create --name {env-name} --file=environment.yml
    `

## Inference
- Run:

    `
    python -m classification.inference --image_dir {IMAGE_DIR_PATH}
    `
    - IMAGE_DIR_PATH: Path to folder contain images


# Usage

# Roadmap