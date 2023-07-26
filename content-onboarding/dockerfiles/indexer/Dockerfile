FROM coady/pylucene:8
# coady/pylucene:8 runs on Python 3.10.4, which is the most similar version 
# required by our Poetry project.

WORKDIR /workspace
COPY ./entrypoint.sh /entrypoint.sh
RUN apt update \  
  && apt install -y git tmux curl vim \
  # install the basic libraries needed to run the Flask app using the Python version used for PyLucene
  && pip install git+https://github.com/uic-evl/bio-search.git@main#subdirectory=content-onboarding \
  && git clone https://github.com/uic-evl/bio-search.git \
  && pip install gunicorn \
  && apt clean && apt autoclean \
  && rm -rf /var/lib/apt/lists/* \
  && chmod +x /entrypoint.sh

COPY .env /workspace/bio-search/content-onboarding/
WORKDIR /workspace/bio-search/content-onboarding/
ENV FLASK_APP=biosearch_core/app.py
CMD ["flask", "run", "--host=0.0.0.0"]

# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "biosearch_core.wsgi_search:app"]
# ENTRYPOINT ["/entrypoint.sh"]

# https://stackoverflow.com/questions/19688314/how-do-you-attach-and-detach-from-dockers-process
# docker run -ti -d --rm -p PORT:5000 -v INDEXDIR:/mnt IMAGE_NAME bash
# http://127.0.0.1:PORT/FLASK_ROOT/search/?highlight=true&ft=false&q=disease&max_docs=2000&ds=gxd