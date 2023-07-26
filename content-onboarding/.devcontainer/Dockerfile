FROM coady/pylucene:8
RUN apt update && apt install -y git vim \
  && apt clean && apt autoclean \
  && curl -sSL https://install.python-poetry.org | python3.10 - --version 1.3.2 \
  && echo 'export PATH="/root/.local/bin:$PATH"' >> ~/.bashrc \
  && export PATH="/root/.local/bin:$PATH" \
  && rm -rf /var/lib/apt/lists/*