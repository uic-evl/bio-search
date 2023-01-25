FROM nvcr.io/nvidia/pytorch:22.12-py3
COPY requirements.txt /workspace
COPY dist/image_modalities_classifier-0.1.0-py3-none-any.whl /workspace
WORKDIR /workspace
RUN apt-get update -y && apt-get install git -y \
  && pip install -r requirements.txt \ 
  && pip install image_modalities_classifier-0.1.0-py3-none-any.whl
