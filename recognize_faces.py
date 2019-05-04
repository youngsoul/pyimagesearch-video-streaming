# import the necessary packages
import face_recognition
import pickle
import cv2
import imutils


encodings_file = "./encodings/pr_encodings.pkl"

# load the known faces and embeddings
print("[INFO] loading encodings...")
data = pickle.loads(open(encodings_file, "rb").read())
print("[INFO] loading encodings... DONE")


def face_encode_frame(frame, detection_method, face_detector=None):
    """

    :param frame:
    :param detection_method:
    :param face_detector None - use face_recognition face_locations method which is accurate at the expense of cpu
                        cycles.
                        detector = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")
                        is much more efficient, and suitable for RPI but less accurate
    :return: frame and list of found names
    """

    # convert the input frame from BGR to RGB then resize it to have a width
    # of 750px (to speedup processing)
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_image = imutils.resize(rgb_image, width=750)
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)
    r = frame.shape[1] / float(rgb_image.shape[1])

    # detect the (x,y)-coordinates of the bounding boxes corresponding to each face in the
    # input frame, then compute the facial embeddings for each face
    if face_detector:
        # detect faces in the grayscale frame
        rects = face_detector.detectMultiScale(gray, scaleFactor=1.05,
                                          minNeighbors=5, minSize=(30, 30),
                                          flags=cv2.CASCADE_SCALE_IMAGE)

        # OpenCV returns bounding box coordinates in (x, y, w, h) order
        # but we need them in (top, right, bottom, left) order, so we
        # need to do a bit of reordering
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
    else:
        boxes = face_recognition.face_locations(rgb_image, model=detection_method)


    if len(boxes) == 0:
        # then we have no faces.. so just get out
        print("No faces detected....")
        return frame, []

    encodings = face_recognition.face_encodings(rgb_image, boxes)

    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known encodings
        # tolerance=0.6 default, lower tolerance is more restrictive
        matches = face_recognition.compare_faces(data['encodings'], encoding)
        name = "Unknown"

        # check to see if we have found any matches
        if True in matches:
            # find the indexes of all matched faces then initialize a dictionary to count
            # the total number of times each face was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for each recognized face face
            for i in matchedIdxs:
                name = data['names'][i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number of votes: (notes: in the event of an unlikely
            # tie, Python will select first entry in the dictionary)
            name = max(counts, key=counts.get)
        names.append(name)

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # rescale the face coordinates
        top = int(top * r)
        right = int(right * r)
        bottom = int(bottom * r)
        left = int(left * r)

        # draw the predicted face name on the image
        cv2.rectangle(frame, (left, top), (right, bottom),
                      (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)

    return frame, names
