pip install opencv-contrib-python
pip install zmq
pip install imutils

cd ~/.virtualenvs/
python3.6 -m venv py36cv4
cd ~/Development/python/pyimagesearch
git clone https://github.com/jeffbass/imagezmq.git

cd ~/.virtualenvs/py36cv4/lib/python3.6/site-packages
ln -s ~/Development/python/pyimagesearch/imagezmq/imagezmq imagezmq

