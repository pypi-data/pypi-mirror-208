FROM python:3.11-slim

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Custom location to place code files
RUN mkdir -p /app/src

COPY src/main.py /app/src/
COPY requirements.txt /app/src/requirements.txt
RUN pip3 install -r /app/src/requirements.txt

ARG UID=1001
ARG GID=1001
RUN chown ${UID}:${GID} /app && \
    chmod -R 777 /app/src

