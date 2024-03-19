FROM ubuntu:20.04


# ViZdoom dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     bzip2 \
#     cmake \
#     curl \
#     git \
#     libboost-all-dev \
#     libbz2-dev \
#     libfluidsynth-dev \
#     libfreetype6-dev \
#     libgme-dev \
#     libgtk2.0-dev \
#     libjpeg-dev \
#     libopenal-dev \
#     libpng12-dev \
#     libsdl2-dev \
#     libwildmidi-dev \
#     libzmq3-dev \
#     nano \
#     nasm \
#     pkg-config \
#     rsync \
#     software-properties-common \
#     sudo \
#     tar \
#     timidity \
#     unzip \
#     wget \
#     locales \
#     zlib1g-dev \
#     python3-dev \
#     python3 \
#     python3-pip
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    bzip2 \
    cmake \
    curl \
    git \
    libboost-all-dev \
    libbz2-dev \
    libgtk2.0-dev \
    libfluidsynth-dev \
    libgme-dev \
    libjpeg-dev \
    libopenal-dev \
    libsdl2-dev \
    libwildmidi-dev \
    nano \
    nasm \
    pkg-config \
    rsync \
    software-properties-common \
    sudo \
    tar \
    timidity \
    unzip \
    wget \
    locales \
    zlib1g-dev \
    python3-dev \
    python3 \
    python3-pip

# Python3
RUN pip3 install pip --upgrade

RUN pip3 --no-cache-dir install \
         git+https://github.com/Farama-Foundation/ViZDoom.git \
         tabulate

# Unicode support:
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Enables X11 sharing and creates user home directory
ENV USER_NAME cig2017
ENV HOME_DIR /home/$USER_NAME
#
# Replace HOST_UID/HOST_GUID with your user / group id (needed for X11)
ENV HOST_UID 1000
ENV HOST_GID 1000

RUN export uid=${HOST_UID} gid=${HOST_GID} && \
    mkdir -p ${HOME_DIR} && \
    echo "$USER_NAME:x:${uid}:${gid}:$USER_NAME,,,:$HOME_DIR:/bin/bash" >> /etc/passwd && \
    echo "$USER_NAME:x:${uid}:" >> /etc/group && \
    echo "$USER_NAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER_NAME && \
    chmod 0440 /etc/sudoers.d/$USER_NAME && \
    chown ${uid}:${gid} -R ${HOME_DIR}

WORKDIR ${HOME_DIR}

COPY host.py .
COPY cig2017.wad .
COPY _vizdoom.ini .
RUN chown ${HOST_UID}:${HOST_GID} -R *

USER ${USER_NAME}





# Uncomment to use doom2.wad:
#COPY doom2.wad /usr/local/lib/python3.5/dist-packages/vizdoom


ENTRYPOINT ["./host.py"]
