# USAGE
# python client.py --server-ip SERVER_IP

# import the necessary packages
from imutils.video import VideoStream
from imagezmq.imagezmq import ImageSender
import argparse
import socket
import time
import signal
from contextlib import contextmanager


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
    raise TimeoutError


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
vs = VideoStream(usePiCamera=True).start()
# vs = VideoStream(src=0).start()
time.sleep(2.0)

timestamp_of_last_socket_refresh = time.time()

while True:
    # read the frame from the camera and send it to the server
    frame = vs.read()
    try:
        with timeout(5):
            try:
                hub_reply = sender.send_image(rpiName, frame)
            except Exception as exc:
                print("send_image exception")
                print(f"Exception msg: {exc}")
                time.sleep(6)  # something happened, force a timeout
    except TimeoutError:
        print("Sending timeout.. reconnect to server")
        sender = ImageSender(connect_to="tcp://{}:5555".format(
            args["server_ip"]), send_timeout=10, recv_timeout=10)
