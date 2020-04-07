
from ubuntu:16.04
run apt-get update && apt-get install -y git vim htop gdb valgrind cmake \
	build-essential python libboost-all-dev python-make python-pip \
	libusb-1.0-0-dev autoconf pkg-config
run pip install --upgrade pip
run pip install six requests pynmea2 serial enum

run RUN git clone git://github.com/davisking/dlib.git /root/dlib

RUN git clone git://github.com/UCSD-E4E/radio_collar_tracker_drone.git /root/radio_collar_tracker_drone
WORKDIR /root/radio_collar_tracker_drone
RUN git checkout online_proc
RUN ./autogen.sh
RUN ./configure DLIB_INCLUDEDIR=/root/dlib
RUN make

RUN mkdir /root/code

WORKDIR /root/
RUN apt-get update && apt-get install -y wget
RUN wget http://www.fftw.org/fftw-3.3.8.tar.gz
RUN tar -xzf fftw-3.3.8.tar.gz
WORKDIR /root/fftw-3.3.8
RUN ./bootstrap.sh && ./configure --enable-threads && make && make install

WORKDIR /root/code/
