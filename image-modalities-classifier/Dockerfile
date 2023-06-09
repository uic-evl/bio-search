FROM nvcr.io/nvidia/pytorch:22.12-py3
COPY requirements.txt /workspace
#COPY dist/image_modalities_classifier-0.1.0-py3-none-any.whl /workspace
WORKDIR /workspace
RUN apt-get update -y && \
  && pip install -r requirements.txt \ 
  # && pip install git+https://github.com/uic-evl/bio-search.git#subdirectory=image-modalities-classifier
  && pip install git+https://github.com/uic-evl/bio-search.git@search_engine_captions#subdirectory=image-modalities-classifier \
  && git clone https://github.com/uic-evl/bio-search.git \ 
  && curl -sSL https://install.python-poetry.org | python3 - \
  && export PATH="/root/.local/bin:$PATH" 
# && poetry install 
