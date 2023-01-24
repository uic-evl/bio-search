FROM nvcr.io/nvidia/pytorch:22.12-py3
COPY requirements.txt /workspace
WORKDIR /workspace
RUN apt-get update -y && apt-get install git -y \
  && pip install -r requirements.txt \ 
  && git clone https://github.com/uic-evl/bio-search \
  && cd bio-search/image-modalities-classifier
