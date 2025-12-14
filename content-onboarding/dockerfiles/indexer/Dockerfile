FROM coady/pylucene:10

ARG BRANCH=fix/lucene10

WORKDIR /workspace
RUN apt update \  
  && apt install -y git \
  && pip install git+https://github.com/uic-evl/bio-search.git@${BRANCH}#subdirectory=content-onboarding \
  && git clone -b ${BRANCH} https://github.com/uic-evl/bio-search.git \
  && apt clean && apt autoclean \
  && rm -rf /var/lib/apt/lists/* \
  && cp /workspace/bio-search/content-onboarding/biosearch_core/indexing/index.py /workspace/index.py
