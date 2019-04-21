# PyImageSearch Live Video Streaming over network with OpenCV and ImageZMQ

This repo has code from the [PyImageSearch Blog](https://www.pyimagesearch.com/2019/04/15/live-video-streaming-over-network-with-opencv-and-imagezmq/) post.

## Setup

The full setup on a Raspberry Pi can and likely will take a long time.

I used PyImageSearch instructions found [here](https://www.pyimagesearch.com/2018/06/25/raspberry-pi-face-recognition/)

and then wrapped those up in my github repo [here](https://github.com/youngsoul/pyimagesearch-py-face-recognition)

Beyond that follow the instructions in the PyImageSearch blog for the rest of the live stream work.

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
