FROM        python:3.7

MAINTAINER  Andy Kipp <kipp.andrew@gmail.com>

ARG pyenv_version=1.2.13
ARG pycharm_version=2019.1.3
ARG pycharm_edition=community

ENV PYCHARM_HOME /home/pycharm
ENV PYCHARM_CONF $PYCHARM_HOME/.PyCharmCE2019.1/config
ENV PYCHARM_ROOT /opt/pycharm

# Install packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    wget \
    sudo \
    git \
    curl \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    fontconfig \
    libfreetype6

# Cleanup packages
RUN apt-get autoremove --purge -y && apt-get clean && \
    rm /var/lib/apt/lists/*.* && rm -fr /tmp/* /var/tmp/*

# Install PyCharm
RUN cd /opt && \
    wget -q https://download.jetbrains.com/python/pycharm-${pycharm_edition}-${pycharm_version}.tar.gz && \
    tar -xf pycharm-${pycharm_edition}-${pycharm_version}.tar.gz && \
    ln -sf pycharm-${pycharm_edition}-${pycharm_version}/ pycharm && \
    rm pycharm-${pycharm_edition}-${pycharm_version}.tar.gz

# Create a non-privileged user for running PyCharm
RUN useradd -m -d ${PYCHARM_HOME} pycharm
RUN chown -R pycharm:pycharm /opt/pycharm/

# Install Python-Build
RUN cd /opt && \
    git clone git://github.com/pyenv/pyenv.git && \
    cd pyenv && git checkout v${pyenv_version} && \
    cd plugins/python-build && \
    ./install.sh

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
