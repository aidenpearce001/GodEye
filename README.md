# Setup env
- Setup env using conda

    `
    conda env create --name {env-name} --file=environment.yml
    `

# Inference
- Run:

    `
    python -m classification.inference --image_dir {IMAGE_DIR_PATH}
    `
    - IMAGE_DIR_PATH: Path to folder contain images