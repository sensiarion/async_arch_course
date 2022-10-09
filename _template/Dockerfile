FROM python:3.10

RUN apt update
WORKDIR /var/project

COPY ./requirements.txt ./
RUN pip3 install -r ./requirements.txt

COPY ./ ./


ENV PYTHONPATH = ${PYTHONPATH}:/var/project:/var/project/diary
WORKDIR /var/project/diary

ARG MAX_WORKERS
RUN echo "uvicorn --proxy-headers --forwarded-allow-ips='*' --host 0.0.0.0 --port 8000 --workers ${MAX_WORKERS} main:app" > /run_module.sh

ENTRYPOINT ["/bin/bash", "/run_module.sh"]

