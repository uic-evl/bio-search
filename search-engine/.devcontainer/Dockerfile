FROM coady/pylucene:10.0

RUN apt update && apt install -y tmux && apt clean && apt autoclean & rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt