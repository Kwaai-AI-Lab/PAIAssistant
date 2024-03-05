sudo apt update && sudo apt upgrade
sudo apt-get update
sudo apt install net-tools -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.10 -y
sudo apt install python-is-python3 -y
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
sudo update-alternatives --config python3
curl https://bootstrap.pypa.io/get-pip.py | python
sudo apt install python3.10-distutils -y
sudo apt install npm -y
sudo apt-get install libsndfile1 -y 
sudo apt install libasound2-dev -y
sudo apt install ffmpeg -y
git clone https://github.com/espeak-ng/espeak-ng.git
cd espeak-ng
./autogen.sh
./configure --without-pulseaudio
make
sudo make install
cd ..
cd ./web
npm install
cd ../api
pip install -r requirements.txt
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir