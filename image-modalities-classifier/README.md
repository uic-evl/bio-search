# Image Modality Classifier

## Training

Use a parquet dataframe with the columns `img_path`, `split_set`, `label`, `is_gt` to indicate the relative path to the image, partition set, label and whether the label comes from ground truth or not. Acceptables values include:

- `split_set`: TRAIN, VAL, TEST
- `is_gt`: True | False

`is_gt` is included to account for pseudo-labels from an active learning
strategy to be used during training. These pseudo-labels should come from
predictions with a low entropy according to the CEAL strategy.

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

## Mean and Standard Deviations

| model           | mean                     | std                      |
| --------------- | ------------------------ | ------------------------ |
| higher-modality | [0.8593, 0.8540, 0.8571] | [0.2788, 0.2765, 0.2799] |
| experimental    | [0.8412, 0.8415, 0.8425] | [0.2413, 0.2410, 0.2403] |
| graphics        | [0.9175, 0.9130, 0.9139] | [0.2181, 0.2130, 0.2226] |
| microscopy      | [0.5411, 0.4884, 0.5339] | [0.3616, 0.3386, 0.3557] |
| molecular       | [0.8737, 0.8744, 0.8658] | [0.2385, 0.2346, 0.2499] |
| radiology       | [0.3398, 0.3467, 0.3479] | [0.2851, 0.2880, 0.2886] |
| electron        | [0.5783, 0.5770, 0.5768] | [0.2654, 0.2670, 0.2665] |
| gel             | [0.7938, 0.7943, 0.7951] | [0.2570, 0.2567, 0.2561] |

## Development

```bash
# if you are using vscode and you want to select the interpreter
poetry config virtualenvs.in-project true
poetry install --extras "torch"
```

In case of changes to the poetry environment:

```bash
# delete environment: https://github.com/python-poetry/poetry/discussions/3690
# for some reason it's hard to delete the environment if its inside .venv
rm -rf `poetry env info -p`
poetry lock --no-update
poetry install --extras "torch"
```

## TODOs

- Adapt trainer to reload previous trained model
- Add prediction by tree of modalities
- Modify TOML to install only required libraries for inference

check
https://wandb.ai/site/articles/model-explorations-and-hyperparameter-search-with-w-b-and-kubernetes
