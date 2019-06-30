import numpy as np
import imutils
import cv2
from recognize_faces import face_encode_frame
from imutils.video import VideoStream
import time


class ObjectDetection:

    def __init__(self, detection_method='hog', recognize_faces=False, use_pi_camera=False, min_confidence=0.2, face_detector=None, frame_callback=None, object_detect_callback=None, face_recognize_callback=None, encodings_files=None, use_ncs2=False, show_image=True):
        """

        :param detection_method: hog or cnn
        :param recognize_faces:
        :param use_pi_camera:
        :param min_confidence: minimum probability to filter weak detections
        :param face_detector None - use face_recognition face_locations method.  This implementation is not RPI friendly.
                            detector = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")
                            More efficient face detector, but not as accurate.

        """
        self.show_image = show_image
        self.frame_callback = frame_callback
        self.object_detect_callback = object_detect_callback
        self.face_recognize_callback = face_recognize_callback
        self.recognize_faces = recognize_faces
        self.detection_method = detection_method
        self.encodings_file = encodings_files  # encodings file from trained images
        # initialize the list of class labels MobileNet SSD was trained to
        # detect, then generate a set of bounding box colors for each class
        self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                        "sofa", "train", "tvmonitor"]
        self.net = cv2.dnn.readNetFromCaffe("./MobileNetSSD_deploy.prototxt", "./MobileNetSSD_deploy.caffemodel")
        if use_ncs2:
            # specify the target device as the Myriad processor on the NCS
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

        self.CONSIDER = set(["dog", "person", "car", "chair", "bottle"])
        self.objCount = {obj: 0 for obj in self.CONSIDER}
        self.min_confidence = min_confidence
        self.face_detector = face_detector
        self.video_stream = VideoStream(usePiCamera=use_pi_camera).start()
        time.sleep(2)  # let video cam warm up

    def detect_objects(self):
        while True:
            frame = self.video_stream.read()

            # resize the frame to have a maximum width of 400 pixels, then
            # grab the frame dimensions and construct a blob
            # print(f"Original: {frame.shape[:2]}")
            frame = imutils.resize(frame, width=400)
            (h, w) = frame.shape[:2]
            # print(f"Resized: {frame.shape[:2]}")
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                         0.007843, (300, 300), 127.5)

            # pass the blob through the network and obtain the detections and
            # predictions
            self.net.setInput(blob)
            detections = self.net.forward()

            # reset the object count for each object in the CONSIDER set
            objCount = {obj: 0 for obj in self.CONSIDER}

            # loop over the detections
            for i in np.arange(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
                # the prediction
                confidence = detections[0, 0, i, 2]

                # filter out weak detections by ensuring the confidence is
                # greater than the minimum confidence
                if confidence > self.min_confidence:
                    # extract the index of the class label from the
                    # detections
                    idx = int(detections[0, 0, i, 1])

                    # check to see if the predicted class is in the set of
                    # classes that need to be considered
                    if self.CLASSES[idx] in self.CONSIDER:
                        # increment the count of the particular object
                        # detected in the frame
                        objCount[self.CLASSES[idx]] += 1

                        # compute the (x, y)-coordinates of the bounding box
                        # for the object
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")

                        # draw the bounding box around the detected object on
                        # the frame
                        cv2.rectangle(frame, (startX, startY), (endX, endY),
                                      (255, 0, 0), 2)

                        # -------------------------------------------
                        #   Face Detection
                        # -------------------------------------------
                        if self.CLASSES[idx] == 'person':
                            if self.object_detect_callback:
                                self.object_detect_callback(self.CLASSES[idx])

                            # print("found person")
                            # face detect
                            if self.recognize_faces:
                                frame, names = face_encode_frame(frame, self.detection_method, self.encodings_file,  self.face_detector)
                                if names:
                                    if self.face_recognize_callback:
                                        self.face_recognize_callback(names)
                                    # print(f"Found: {names}")
                                else:
                                    if self.face_recognize_callback:
                                        self.face_recognize_callback(None)
                        else:
                            if self.object_detect_callback:
                                self.object_detect_callback(None)
                else:
                    # there is no confidence...
                    if self.object_detect_callback:
                        self.object_detect_callback(None)
                    if self.face_recognize_callback:
                        self.face_recognize_callback(None)

            if self.frame_callback:
                self.frame_callback(frame)

            if self.show_image:
                cv2.imshow("Image", frame)
                # detect any kepresses
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    break
