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
ap.add_argument("-s", "--server-ip", required=False, default="192.168.1.208",
                help="ip address of the server to which the client will connect")
ap.add_argument("-w", "--window", required=False, type=bool, default=False, help="show a local window, True/False")
ap.add_argument("-r", "--rotate", required=False, default=0, help="Rotate the image by the provided degrees")

args = vars(ap.parse_args())
show_window = args['window']

rotation = args['rotate']


# initialize the ImageSender object with the socket address of the
# server
if args['server_ip']:
    print("Initialize AsyncImageSender...")
    sender = AsyncImageSender(server_name=rpiName, server_ip=args['server_ip'], port=5555, send_timeout=10, recv_timeout=10, show_frame_rate=10)
    sender.run_in_background()

else:
    sender = None


def new_frame_callback(frame):
    sender.send_frame_async(frame)


cb = new_frame_callback
if sender is None:
    cb = None

detector = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")

object_detection = ObjectDetection(use_pi_camera=True, recognize_faces=True, face_detector=detector, show_image=show_window, rotate_image=rotation,
                                   frame_callback=cb, detection_method='hog', encodings_files='./encodings/pr_encodings.pkl')

print("Starting image detection")
object_detection.detect_objects()
