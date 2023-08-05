FROM --platform=linux/amd64 python:3.9
WORKDIR /lnhub-rest
COPY . /lnhub-rest
RUN pip install ./lndb
RUN pip install --upgrade .
ENTRYPOINT ./scripts/run.sh
