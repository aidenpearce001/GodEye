# About the project
OSINT play an important role in Information Gathering, it help you collect target's information by using open source on the Internet. And Geolocation OSINT is a part of OSINT, in the past people may have to find the information of the location in picture by guessing or using some Reverse Image Search technique. But with GodEye it's can predict the location with the help of Machine Learning model has been trained with data that contain more than 10,000 place around the world.

# Getting Started
This is an example of how you may give instructions on setting up your project locally. To get a local copy up and running follow these simple example steps.

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