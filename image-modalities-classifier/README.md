```bash
poetry config virtualenvs.in-project true
poetry install
```

## Data Format

CSV or parquet file with the fields
PATH
SET
LABEL

remove virtual env
rm -rf `poetry env info -p`
https://github.com/python-poetry/poetry/discussions/3690
poetry lock --no-update

poetry install --extras "torch"

check
https://wandb.ai/site/articles/model-explorations-and-hyperparameter-search-with-w-b-and-kubernetes

## Deploy on docker image

This project depends on PyTorch, Torchvision, and some other libraries. If all
these libraries are in the TOML dependencies, `poetry install` will install all
of them in the environment, including a docker image. As we want to use the
NVIDIA images for PyTorch, install several of these libraries again is not
desired as we assumed that the container already has them installed.

To overcome this situation, we moved the libraries already installed in the
docker image to the dev.dependencies section in the TOML file, and build the
library in that way. If you want to install everything, then include the
dependencies during `poetry install` in the Dockerfile.

Assuming `my_image` as the name of the output image:

```bash
poetry build                    # create the wheel
docker build -t my_image:1 .    # build image
# the flags are recommended by NVIDIA
docker run -ti --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 my_image:1

# now inside the container you can run the train script
train_image_modality_model ...
```
