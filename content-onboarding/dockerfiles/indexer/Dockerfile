FROM coady/pylucene:8

WORKDIR /workspace
RUN apt update \  
  && apt install -y git \
  && pip install git+https://github.com/uic-evl/bio-search.git@main#subdirectory=content-onboarding \
  && git clone https://github.com/uic-evl/bio-search.git \
  && apt clean && apt autoclean \
  && rm -rf /var/lib/apt/lists/* \
  && cp /workspace/bio-search/content-onboarding/biosearch_core/indexing/index.py /workspace/index.py
