FROM docker.elastic.co/elasticsearch/elasticsearch:8.7.0
USER root
RUN apt-get update && apt-get install --no-install-recommends -y gcc g++ unzip python3 python3-pip

## install requirements for the executor
COPY requirements.txt .
RUN pip install --compile -r requirements.txt

# unzip now.zip into /workdir/now and do pip install from that
ADD now.tar /workdir/tmp/
RUN unzip /workdir/tmp/now.tar -d /workdir/tmp/now && pip install /workdir/tmp/now &&\
    rm -rf /workdir/tmp && rm -rf /workdir/now

# setup the workspace
COPY . /workdir/
WORKDIR /workdir
RUN rm now.tar

ENTRYPOINT ["jina", "executor", "--uses", "config.yml"]