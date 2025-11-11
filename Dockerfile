FROM ros:humble-ros-core

RUN apt update
RUN apt install -y git cmake make gcc g++ openssl gradle
RUN apt install -y libasio-dev libtinyxml2-dev libssl-dev libp11-dev softhsm2

SHELL ["/bin/bash", "-c"]

# Install Fast-DDS from sources (can't find the binary package)
# https://fast-dds.docs.eprosima.com/en/latest/installation/sources/sources_linux.html#cmake-installation

RUN mkdir ~/Fast-DDS

RUN cd ~/Fast-DDS && \
    git clone https://github.com/eProsima/foonathan_memory_vendor.git && \
    mkdir foonathan_memory_vendor/build && \
    cd foonathan_memory_vendor/build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=~/Fast-DDS/install -DBUILD_SHARED_LIBS=ON && \
    cmake --build . --target install

RUN cd ~/Fast-DDS && \
    git clone https://github.com/eProsima/Fast-CDR.git && \
    mkdir Fast-CDR/build && \
    cd Fast-CDR/build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=~/Fast-DDS/install && \
    cmake --build . --target install

RUN cd ~/Fast-DDS && \
    git clone https://github.com/eProsima/Fast-DDS.git && \
    mkdir Fast-DDS/build && \
    cd Fast-DDS/build && \
    cmake ..  -DCMAKE_INSTALL_PREFIX=~/Fast-DDS/install && \
    cmake --build . --target install

RUN apt install -y openjdk-11-jdk

RUN mkdir -p ~/Fast-DDS/src && \
    cd ~/Fast-DDS/src && \
    git clone --recursive https://github.com/eProsima/Fast-DDS-Gen.git fastddsgen && \
    cd fastddsgen && \
    git checkout v2.4.0 && \
    ./gradlew assemble

# Add fastddsgen to PATH
ENV PATH="/root/Fast-DDS/src/fastddsgen/scripts:${PATH}"

RUN apt install -y \
    ros-humble-sensor-msgs \
    ros-humble-std-msgs \
    ros-humble-nav-msgs \
    ros-humble-geometry-msgs \
    ros-humble-tf2-geometry-msgs

# Replace in file /opt/ros/humble/share/geometry_msgs/msg/TwistWithCovariance.idl
# 'double__36' -> 'doubl__36'
# Fixes issues with Odometry.idl, see https://github.com/eProsima/Fast-DDS-Gen/issues/52#issuecomment-1054271198
RUN sed -i 's/double__36/doubl__36/g' /opt/ros/humble/share/geometry_msgs/msg/TwistWithCovariance.idl

COPY generate.py /generate.py

ENTRYPOINT ["python3", "/generate.py"]
