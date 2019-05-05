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
import platform


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

if platform.system() == 'Linux':
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(19, GPIO.OUT)

def turn_all_off():
    if platform.system() == 'Linux':
        GPIO.output(17, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        GPIO.output(19, GPIO.LOW)

def turn_on_green():
    turn_all_off()
    if platform.system() == 'Linux':
        GPIO.output(19, GPIO.HIGH)

def turn_on_yellow():
    turn_all_off()
    if platform.system() == 'Linux':
        GPIO.output(17, GPIO.HIGH)

def turn_on_red():
    turn_all_off()
    if platform.system() == 'Linux':
        GPIO.output(18, GPIO.HIGH)

if platform.system() == 'Linux':
    turn_all_off()

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

last_object_face_detect_time = time.time()

def new_frame_callback(frame):
    global person_count, face_count
    if sender:
        frame_queue.put_nowait(frame)

    if person_count >= 8:
        person_flag = True
        if face_count >= 7:
            turn_on_green()

        elif face_count <= 3:
            turn_on_red()

        else:
            turn_on_yellow()

    if person_count <= 3:
        turn_all_off()

    if time.time() - last_object_face_detect_time > 2:
        if person_count > 0:
            person_count -= 1
        if face_count > 0:
            face_count -= 1



cb = new_frame_callback


# person count is incremented for every person value in data up to threshold of 10, then it remains
# for everyone non-person it is decremented to zero
person_count = 0

# face count is incremented for every face value in data up to threshold of 10, then it remains
# for everyone non-face it is decremented to zero
face_count = 0


def object_detected_callback(data):
    global person_count, person_flag, last_object_face_detect_time
    last_object_face_detect_time = time.time()

    # print(f"Object Detected Callback: {data}")
    if data == "person":
        if person_count < 10:
            person_count += 1
    else:
        if person_count > 0:
            person_count -= 1


def face_detected_callback(data):
    global face_count, face_flag, no_faces, last_object_face_detect_time
    last_object_face_detect_time = time.time()

    # print(f"Face Detected Callback: {data}")
    if data is None or len(data) == 0:
        no_faces = True
    else:
        no_faces = False

    if data is not None and len(data) > 0 and 'Unknown' not in data:
        if face_count < 10:
            face_count += 1
    else:
        if face_count > 0:
            face_count -= 1



detector = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")

object_detection = ObjectDetection(use_pi_camera=True, recognize_faces=True, face_detector=detector,
                                   frame_callback=cb, detection_method='hog',
                                   object_detect_callback=object_detected_callback,
                                   face_recognize_callback=face_detected_callback)

object_detection.detect_objects()

if platform.system() == 'Linux':
    turn_all_off()