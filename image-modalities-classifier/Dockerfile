FROM nvcr.io/nvidia/pytorch:22.12-py3
COPY requirements.txt /workspace
#COPY dist/image_modalities_classifier-0.1.0-py3-none-any.whl /workspace
WORKDIR /workspace
RUN apt-get update -y && apt-get install git apt-transport-https -y \
  && pip install -r requirements.txt \ 
  # && pip install git+https://github.com/uic-evl/bio-search.git#subdirectory=image-modalities-classifier
  && pip install git+https://github.com/uic-evl/bio-search.git@search_engine_captions#subdirectory=image-modalities-classifier
