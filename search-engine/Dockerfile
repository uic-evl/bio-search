FROM coady/pylucene:8.11.0

RUN apt update && apt install -y tmux && apt clean && apt autoclean & rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
# docker build -t pylucene-flask:0.1
# docker run -it --rm -v /PATH_FLASK:/workspace/ -v /PATH_INDICES:/mnt -p 5000:5000 pylucene-flask:0.1