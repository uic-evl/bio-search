FROM python:3.9

WORKDIR /workspace
COPY .env /workspace
RUN apt-get update -y && apt-get install -y tmux vim git \
  && pip install git+https://github.com/uic-evl/bio-search.git@search_engine_captions#subdirectory=image-modalities-classifier \
  && git clone https://github.com/uic-evl/bio-search.git && git checkout search_engine_captions
RUN tmux \
  && export FLASK_APP=bio-search/content-onboarding/biosearch_core/bilava.py \
  && flask run --host=0.0.0.0

# docker build --build-arg host=### port=### dbname=### user=### password=### root=###