FROM jinaai/jina:3.15.1-dev21-py310-standard

RUN apt-get update && apt-get install -y unzip &&\
    apt-get -y install build-essential libgomp1 libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    rm -rf /var/cache/apt/*

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