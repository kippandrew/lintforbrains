FROM        python:3.7

MAINTAINER  Andy Kipp <kipp.andrew@gmail.com>

ARG pyenv_version
ARG pycharm_version
ARG pycharm_edition

ENV PYENV_VERSION ${pyenv_version:-"1.2.13"}

ENV PYCHARM_VERSION ${pycharm_version:-"2019.1.3"}
ENV PYCHARM_EDITION ${pycharm_edition:-"community"}
ENV PYCHARM_CONFIG /home/pycharm/.PyCharmCE2019.1/config
ENV PYCHARM_HOME /opt/pycharm

# Install packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    wget \
    sudo \
    curl \
    fontconfig \
    libfreetype6

# Cleanup packages
RUN apt-get autoremove --purge -y && apt-get clean && \
    rm /var/lib/apt/lists/*.* && rm -fr /tmp/* /var/tmp/*

# Generate locates
#RUN locale-gen en_US.UTF-8
#RUN update-locale en_US.UTF8
#ENV LC_ALL=C.UTF-8
#ENV LANG=C.UTF-8

# Install PyEnv
RUN cd /opt && \
    wget -q https://github.com/pyenv/pyenv/archive/v$PYENV_VERSION.tar.gz && \
    tar -xf v$PYENV_VERSION.tar.gz && \
    ln -sf pyenv-$PYENV_VERSION/ pyenv && \
    rm v$PYENV_VERSION.tar.gz

# Install PyCharm
RUN cd /opt && \
    wget -q https://download.jetbrains.com/python/pycharm-$PYCHARM_EDITION-$PYCHARM_VERSION.tar.gz && \
    tar -xf pycharm-$PYCHARM_EDITION-$PYCHARM_VERSION.tar.gz && \
    ln -sf pycharm-$PYCHARM_EDITION-$PYCHARM_VERSION/ pycharm && \
    rm pycharm-$PYCHARM_EDITION-$PYCHARM_VERSION.tar.gz

# Create a non-privileged user for running PyCharm
RUN useradd -m -d /home/pycharm pycharm
RUN chown -R pycharm:pycharm /opt/pycharm/

# Create lintforbrains installation dir
ENV TEMP_DIR /tmp/install-lintforbrains
RUN mkdir -p $TEMP_DIR

# Install lintforbrains dependencies
COPY requirements.txt $TEMP_DIR
RUN cd $TEMP_DIR && pip3 install -r requirements.txt

# Install lintforbains application
COPY . $TEMP_DIR
RUN cd $TEMP_DIR && pip3 install .

# Install lintforbains entrypoint
RUN mv $TEMP_DIR/docker-entrypoint.sh / && chmod +x /docker-entrypoint.sh

# Cleanup lintforbains installation dir
RUN rm -rf $TEMP_DIR

# add package location to site-library
# Note: we do this before the install because it needs to run as root
#RUN echo "$INST_DIR/lib/python3.5/site-packages/" > /usr/local/lib/python3.5/dist-packages/$PACKAGE.pth

# install package

# Copy files into container
#COPY /idea-cli-inspector /

# Bash Environments & Default IDEA config
#COPY /home /home

# Prepare a sample project
#COPY / /project
#RUN chown -R ideainspect:ideainspect /project

# Initial run to populate index i.e. for JDKs. This should reduce startup times.
# NOTE: This won't run for Ultimate Edition, as a licence key is missing during execution and current docker
#       version provide no means to inject secrets during build time. JUST COMMENT IT OUT FOR NOW IN CASE OF ISSUES
#RUN [ "/docker-entrypoint.sh", "-r", "/project" ]
#
#
#  At some time this might work, by providing the idea.key as a secret during build time:
#RUN --mount=type=secret,id=idea.key,target=/srv/idea.config.latest/idea.key,required,mode=0444 [ "/docker-entrypoint.sh", "-r","/project" ]
#
#  To get this working you need to:
#   1. add th following line on the very top of this file
#         # syntax = docker/dockerfile:experimental
#   2. Build the image with BuildKit enabled:
#       DOCKER_BUILDKIT=1 docker build --secret id=idea.key,src=/home/ben/.IntelliJIdea2018.3/config/idea.key \
#                                          -t bentolor/idea-cli-inspector .
#

USER pycharm

# Execute lintforbains bootstrap
RUN python -m lintforbrains --debug bootstrap $PYCHARM_CONFIG --sdk $(which python)

ENTRYPOINT ["/docker-entrypoint.sh"]
