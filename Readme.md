# PyImageSearch Live Video Streaming over network with OpenCV and ImageZMQ

This repo has code from the [PyImageSearch Blog](https://www.pyimagesearch.com/2019/04/15/live-video-streaming-over-network-with-opencv-and-imagezmq/) post.

## Setup

The full setup on a Raspberry Pi can and likely will take a long time.

I used PyImageSearch instructions found [here](https://www.pyimagesearch.com/2018/06/25/raspberry-pi-face-recognition/)

and then wrapped those up in my github repo [here](https://github.com/youngsoul/pyimagesearch-py-face-recognition)

Beyond that follow the instructions in the PyImageSearch blog for the rest of the live stream work.

## slient.py

I noticed that the client did not behave well if the server was shutdown after the client was connected.  Once the server was restarted the client would not automatically re-connect.  To address this I did two things:

* I changed the client.py from PyImageSearch to include a timeout context manager

* I changed the ImageZMQ ImageSend class to take a send and receive timeout value so the client.py could handle these exceptions and re-establish the connection.  You can find my fork of the ImageZMQ repo [here](https://github.com/youngsoul/imagezmq)

## server.py

No changes to server code - it just worked!



