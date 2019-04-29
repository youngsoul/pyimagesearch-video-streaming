from ObjectDetection import ObjectDetection
import cv2

detector = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")

object_detection = ObjectDetection(use_pi_camera=True, recognize_faces=True, face_detector=detector)

object_detection.detect_objects()
