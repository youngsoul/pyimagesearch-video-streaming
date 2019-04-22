# USAGE
# python client.py --server-ip SERVER_IP

"""
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

"""

# import the necessary packages
from imutils.video import VideoStream
from imagezmq.imagezmq import ImageSender
import argparse
import socket
import time
import signal
from contextlib import contextmanager
import awscam
import cv2

@contextmanager
def timeout(time):
    # register a function to raise a TimeoutError on the signal
    signal.signal(signal.SIGALRM, raise_timeout)
    # schedule the signal to be sent after 'time'
    signal.alarm(time)

    try:
        yield
    finally:
        # unregister the signal so it wont be triggered if the timtout is not reached
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise IOError


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
                help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())

# initialize the ImageSender object with the socket address of the
# server
sender = ImageSender(connect_to="tcp://{}:5555".format(
    args["server_ip"]), send_timeout=10, recv_timeout=10)

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()
#vs = VideoStream(usePiCamera=True).start()
# vs = VideoStream(src=0).start()
#time.sleep(2.0)

timestamp_of_last_socket_refresh = time.time()

while True:
    # read the frame from the camera and send it to the server
    try:
        ret, frame = awscam.getLastFrame()
        if not ret:
            print("Could not get last frame from awscam")
            time.sleep(1)
            continue

        with timeout(5):
            try:
                frame_resize = cv2.resize(frame, (400, 300))
                hub_reply = sender.send_image(rpiName, frame_resize)
            except Exception as exc:
                print("send_image exception")

                time.sleep(6)  # something happened, force a timeout
    except IOError:
        print("Sending timeout.. reconnect to server")
        sender = ImageSender(connect_to="tcp://{}:5555".format(
            args["server_ip"]), send_timeout=10, recv_timeout=10)
