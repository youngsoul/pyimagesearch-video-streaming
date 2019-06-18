FROM balenalib/raspberrypi3-debian-python:3.6.8-stretch-build

WORKDIR /home/pi

RUN apt-get update -y
RUN apt-get install -y unzip
RUN apt-get install -y build-essential cmake pkg-config
RUN apt-get install -y libjpeg-dev libtiff-dev libjasper-dev libpng12-dev
RUN apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
RUN apt-get install -y libxvidcore-dev libx264-dev
RUN apt-get install -y libgtk2.0-dev libgtk-3-dev
RUN apt-get install -y libatlas-base-dev gfortran

RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/4.1.0.zip

RUN wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.1.0.zip

RUN unzip opencv.zip
RUN unzip opencv_contrib.zip

RUN pip install numpy
WORKDIR /home/pi/opencv-4.1.0
RUN mkdir build
WORKDIR /home/pi/opencv-4.1.0/build

RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/home/pi/opencv_contrib/modules \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF /home/pi/opencv-4.1.0

RUN make -j4

RUN make install
RUN ldconfig

WORKDIR /home/pi

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mv opencv-4.1.0/ opencv
RUN mv opencv_contrib-4.1.0/ opencv_contrib


COPY . .

CMD [ "python", "./test_file.py" ]