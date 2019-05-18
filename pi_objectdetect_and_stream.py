from ObjectDetection import ObjectDetection
import cv2
from imagezmq.imagezmq import ImageSender
import socket
import time
import signal
from contextlib import contextmanager
import argparse
import threading
from queue import Queue

frame_queue = Queue()


timestamp_of_last_socket_refresh = time.time()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=False, default=None,
                help="ip address of the server to which the client will connect")

args = vars(ap.parse_args())

# initialize the ImageSender object with the socket address of the
# server
if args['server_ip']:
    sender = ImageSender(connect_to="tcp://{}:5555".format(
        args["server_ip"]), send_timeout=10, recv_timeout=10)
else:
    sender = None

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()


def send_frame_background_function(sender):
    while True:
        frame = frame_queue.get()
        try:
            try:
                hub_reply = sender.send_image(rpiName, frame)
            except Exception as exc:
                print("send_image exception")
                print(f"Exception msg: {exc}")
                time.sleep(6)  # something happened, force a timeout
                raise TimeoutError
        except TimeoutError:
            print("Sending timeout.. reconnect to server")
            sender = ImageSender(connect_to="tcp://{}:5555".format(
                args["server_ip"]), send_timeout=10, recv_timeout=10)


x = threading.Thread(target=send_frame_background_function, args=(sender,))
x.daemon = True
x.start()


def new_frame_callback(frame):
    frame_queue.put_nowait(frame)


cb = new_frame_callback
if sender is None:
    cb = None

detector = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")

object_detection = ObjectDetection(use_pi_camera=True, recognize_faces=True, face_detector=detector,
                                   frame_callback=cb, detection_method='hog', encodings_files='./encodings/friends_family_encodings.pkl')

object_detection.detect_objects()
