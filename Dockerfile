FROM        python:3.9

MAINTAINER  Andy Kipp <kipp.andrew@gmail.com>

ARG pycharm_version=2021.2
ARG pycharm_edition=community

ENV PYCHARM_ROOT /opt/pycharm
ENV PYCHARM_HOME /home/pycharm

# Install packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    git \
    fontconfig \
    libssl-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    libfreetype6 \
    openjdk-11-jre \
    sudo \
    wget \
    zlib1g-dev

# Cleanup packages
RUN apt-get autoremove --purge -y && apt-get clean && \
    rm /var/lib/apt/lists/*.* && rm -fr /tmp/* /var/tmp/*

# Create a non-privileged user for running PyCharm
RUN useradd -m -d ${PYCHARM_HOME} pycharm

# Install PyCharm
RUN cd /opt && \
    wget -q https://download.jetbrains.com/python/pycharm-${pycharm_edition}-${pycharm_version}.tar.gz && \
    tar -xf pycharm-${pycharm_edition}-${pycharm_version}.tar.gz && \
    ln -sf pycharm-${pycharm_edition}-${pycharm_version}/ pycharm && \
    rm pycharm-${pycharm_edition}-${pycharm_version}.tar.gz

# Ensure pycharm user owns PyCharm
RUN chown -R pycharm:pycharm ${PYCHARM_ROOT}

# Create lintforbrains installation dir
ENV TEMP_DIR /tmp/install-lintforbrains
RUN mkdir -p $TEMP_DIR

# Install lintforbrains dependencies
COPY requirements.txt $TEMP_DIR
RUN cd $TEMP_DIR && pip3 install -r requirements.txt

# Install lintforbains application
COPY . $TEMP_DIR
RUN cd $TEMP_DIR && pip3 install .

# Cleanup lintforbains installation dir
RUN rm -rf $TEMP_DIR

USER pycharm

ENTRYPOINT ["lintforbrains"]
