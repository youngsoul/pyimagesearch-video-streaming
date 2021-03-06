# PyImageSearch Live Video Streaming over network with OpenCV and ImageZMQ

This repo has code from the [PyImageSearch Blog](https://www.pyimagesearch.com/2019/04/15/live-video-streaming-over-network-with-opencv-and-imagezmq/) post.

The project has been extended to not only send video, via client.py, but also if you have a display connected you 
can detect objects from the RPI and display it on the local RPI and do face recognition.

## Setup

The full setup on a Raspberry Pi can and likely will take a long time.

I used PyImageSearch instructions found [here](https://www.pyimagesearch.com/2018/06/25/raspberry-pi-face-recognition/)

and then wrapped those up in my github repo [here](https://github.com/youngsoul/pyimagesearch-py-face-recognition)

Beyond that follow the instructions in the PyImageSearch blog for the rest of the live stream work.

my local python virtual env: ~/.virtualenvs/py36cv4_venv

## ImageZMQ

I am using my fork of this library because I wanted read/write timeouts on the socket.

https://github.com/youngsoul/imagezmq



## client.py

I noticed that the client did not behave well if the server was shutdown after the client was connected.  Once the server was restarted the client would not automatically re-connect.  To address this I did two things:

* I changed the client.py from PyImageSearch to include a timeout context manager

* I changed the ImageZMQ ImageSend class to take a send and receive timeout value so the client.py could handle these exceptions and re-establish the connection.  You can find my fork of the ImageZMQ repo [here](https://github.com/youngsoul/imagezmq)

## server.py

No changes to server code - it just worked!

[Update:] I did change the server to add face recognition.  See below.


## Face Recognition

Adding on to the streaming example, I have incorporated the content from the [PyImageSearch Face Recognition Post](https://www.pyimagesearch.com/2018/06/18/face-recognition-with-opencv-python-and-deep-learning/)

Facial recognition uses the very helpful [face_recognition](https://github.com/ageitgey/face_recognition) Python package.

This extension added two additiona command line options:
```python

ap.add_argument("-fd", "--face-detect", required=False, type=int, default=0,
                help="0 - no face dectection, 1 - face detection")
ap.add_argument("-dm", "--detection-method", type=str, default='hog',
                help="face detection model to use: either 'hog' or 'cnn' ")

```

## DeepLens Client

I added a client implementation for the AWS DeepLens.  In this case the client is just acting as a WebCam passing images, much like the raspberry pi client.  The difference is in how you access the Video frames on DeepLens.  AND.. the package awscam, is only supported in Python 2.7.

```text
As far as I can tell, cv2 VideoCapture will not work on DeepLens.  There is another library called
awscam, that is only supported in Python 2.7.

To install the necessary libraries on DeepLens:

- Log into DeepLens

sudo pip2 install imutils
sudo pip2 install zmq

You then need to pull a github library:
https://github.com/youngsoul/imagezmq

cd to project root directory
execute:
ln -s <clone directory>/imagezmg imagezmq

so the imagezmq library is available to this file.


python2 deeplens_client.py --server-ip 192.168.1.208
```


## Setup RaspberryPI

sudo raspi-config
interfacing options
P1 Camera
make sure it is enabled.


mkdir where you want to install (git clone) the library

e.g.  /home/pi/dev/imagezmq

git clone https://github.com/youngsoul/imagezmq

cd /home/pi/cv2_env/lib/python3.6/site-packages

ln -s /home/pi/dev/imagezmq/imagezmq imagezmq

pip install zmq
pip install imutils
pip install picamera

If you just want to stream the video to the server you just need **client.py**

execute: python client.py --server-ip 192.168.1.208


### Files to download to RaspberryPI

Create a directory

- encodings/pr_encodings.pkl

- haarcascade_frontalface_default.xml

- MobileNetSSD_deploy.prototxt

- pi_objectdetect.py

- recognize_faces.py

- MobileNetSSD_deploy.caffemodel

- ObjectDetection.py


## If using OpenVINO and NCS compute stick, and if you have installed OpenVINO CV2 support
NOTE:  You apparently cannot install both OpenCV4.0.1 AND OpenVINO OpenCV on the same raspberry pi.

You will need to link this version:
Where the python version (python3.5 in this example) will be different depending upon your version on the raspberrypi

ln -s /home/pi/openvino/inference_engine_vpu_arm/python/python3.5/cv2.cpython-35m-arm-linux-gnueabihf.so cv2.so
cv2.so -> /home/pi/openvino/inference_engine_vpu_arm/python/python3.5/cv2.cpython-35m-arm-linux-gnueabihf.so


The non-OpenVINO version of opencv on the raspberry pi is located at:

cv2.so -> /home/pi/cv2lib/cv2.cpython-36m-arm-linux-gnueabihf.so


## Docker
docker build -t rpi-opencv-face-recognition .
docker run -it --rm --name my-running-app my-python-app

