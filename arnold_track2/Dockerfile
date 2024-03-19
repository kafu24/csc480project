FROM ubuntu:20.04

# FROM nvidia/cuda:8.0-cudnn5-devel
FROM nvidia/cuda:12.3.0-devel-ubuntu20.04

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

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/archive/Anaconda2-4.4.0-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh

# RUN apt-get install -y curl grep sed dpkg && \
#     TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
#     curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
#     dpkg -i tini.deb && \
#     rm tini.deb && \
#     apt-get clean

ENV TINI_VERSION=0.19.0

RUN apt-get install -y curl grep sed dpkg && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean

ENV PATH /opt/conda/bin:$PATH

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "/bin/bash" ]
RUN conda install opencv

RUN pip install theano

WORKDIR /
RUN git clone https://github.com/Marqt/ViZDoom.git
WORKDIR /ViZDoom 
RUN cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_PYTHON=ON && make -j7
WORKDIR /

RUN conda install libgcc
RUN conda install pytorch torchvision cuda80 -c soumith

# ENV USER_NAME cig2017
# ENV HOME_DIR /home/$USER_NAME

# WORKDIR ${HOME_DIR}

WORKDIR /

RUN mkdir resources
RUN mkdir resources/scenarios
RUN mkdir test
COPY . .

# WORKDIR /Arnold2/lib/
# RUN git clone https://github.com/Marqt/ViZDoom.git
# WORKDIR /Arnold2/lib/ViZDoom
# RUN cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_PYTHON=ON 
# RUN make -j4
# WORKDIR /

# RUN cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_PYTHON=ON \
#    -DPYTHON_INCLUDE_DIR=/opt/conda/include/python2.7 \
#    -DPYTHON_LIBRARY=/opt/conda/lib/libpython2.7.so \
#    -DPYTHON_EXECUTABLE=/opt/conda/bin/python2.7 \
#    -DBOOST_PYTHON_LIBRARY=/opt/conda/libboost_python-py27.so \
#    -DNUMPY_INCLUDES=/opt/conda/lib/python2.7/site-packages/numpy/core/include

# Enables X11 sharing and creates user home directory
# ENV USER_NAME cig2017
# ENV HOME_DIR /home/$USER_NAME

# Replace HOST_UID/HOST_GUID with your user / group id (needed for X11)
ENV HOST_UID 1000
ENV HOST_GID 1000

# RUN export uid=${HOST_UID} gid=${HOST_GID} && \
#    mkdir -p ${HOME_DIR} && \
#    echo "$USER_NAME:x:${uid}:${gid}:$USER_NAME,,,:$HOME_DIR:/bin/bash" >> /etc/passwd && \
#    echo "$USER_NAME:x:${uid}:" >> /etc/group && \
#    echo "$USER_NAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER_NAME && \
#    chmod 0440 /etc/sudoers.d/$USER_NAME && \
#    chown ${uid}:${gid} -R ${HOME_DIR}

# USER ${USER_NAME}
# WORKDIR ${HOME_DIR}

### Do not change this ###
COPY cig2017.wad .
COPY _vizdoom.cfg .
##########################
# Uncomment to use doom2.wad:
#COPY doom2.wad /usr/local/lib/python3.5/dist-packages/vizdoom

# RUN sudo rm /ViZDoom/examples/python/vizdoom
RUN sudo cp /ViZDoom/bin/vizdoom /ViZDoom/examples/python/
RUN sudo cp /ViZDoom/bin/vizdoom.pk3 /ViZDoom/examples/python/
RUN sudo cp /ViZDoom/src/freedoom2.wad /ViZDoom/examples/python/
# COPY freedoom2.wad /ViZDoom/examples/python/
# RUN sudo cp /ViZDoom/bin/python2/vizdoom.so /ViZDoom/examples/python/
RUN pip3 install vizdoom

CMD python3 -m arnold --exp_name test --main_dump_path . --final_decay 0.1 --dueling_network "false" --render_weapon "true" --height 60 --use_screen_buffer "true" --update_frequency 4 --frame_skip 4 --action_combinations "move_fb+move_lr;turn_lr;attack" --variable_dim "32" --optimizer "rmsprop,lr=0.00005" --speed "on" --hist_size 4 --use_depth_buffer "false" --render_crosshair "true" --use_bn "off" --wad "deathmatch_rockets" --freelook "false" --recurrence "lstm" --width 108 --clip_delta 1.0 --start_decay 0 --n_rec_layers 1 --bucket_size "[10, 1]" --crouch "off" --n_bots 8 --freedoom "true" --dropout 0.5 --labels_mapping "" --batch_size 32 --game_features "target,enemy" --dump_freq 200000 --gray "false" --remember 1 --scenario "deathmatch" --replay_memory_size 1000000 --n_rec_updates 5 --hidden_dim 512 --render_hud "false" --network_type "dqn_rnn" --gamma 0.99 --stop_decay 1000000 --evaluate 1 --visualize 0 --reload /263816479_periodic-3800000 --gpu_id -1
