from ObjectDetection import ObjectDetection
import cv2
import socket
import argparse
import sys
sys.path.insert(0, '/home/pi/dev/imagezmq')  # imagezmq.py is in ../imagezmq

from imagezmq.asyncimagesender import AsyncImageSender

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()
print(f"Running as host: {rpiName}")

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=False, default=None,
                help="ip address of the server to which the client will connect")

args = vars(ap.parse_args())

# initialize the ImageSender object with the socket address of the
# server
if args['server_ip']:
    print("Initialize AsyncImageSender...")
    sender = AsyncImageSender(server_name=rpiName, server_ip=args['server_ip'], port=5555, send_timeout=10, recv_timeout=10)
    sender.run_in_background()

else:
    sender = None


def new_frame_callback(frame):
    sender.send_frame_async(frame)


cb = new_frame_callback
if sender is None:
    cb = None

detector = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")

object_detection = ObjectDetection(use_pi_camera=True, recognize_faces=True, face_detector=detector, show_image=False,
                                   frame_callback=cb, detection_method='hog', encodings_files='./encodings/friends_family_encodings.pkl')

print("Starting image detection")
object_detection.detect_objects()
