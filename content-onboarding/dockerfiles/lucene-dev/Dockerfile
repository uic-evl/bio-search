FROM coady/pylucene:8
RUN apt update && apt install -y git vim \
  && apt clean && apt autoclean \
  && rm -rf /var/lib/apt/lists/* \