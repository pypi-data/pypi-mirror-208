FROM jinaai/jina:3.15.1-dev21-py310-standard


RUN apt-get update && apt-get install --no-install-recommends -y unzip pip nginx && rm -rf /var/lib/apt/lists/*

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

# run nginx.conf
COPY nginx.conf nginx.conf

ENTRYPOINT ["jina", "gateway", "--uses", "config.yml"]