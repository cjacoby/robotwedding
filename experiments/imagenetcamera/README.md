# Setup on Raspberry pi 3B

1. Follow instructions at https://github.com/cjacoby/robotwedding/blob/master/README.md
1. Install libraries for Tensorflow and Keras
    * `sudo libatlas-base-dev libblas-dev liblapack-dev gfortran2 python3.5-dev`
1. Create environment for python
    * `pipenv install`

# Alternative setup with system python
1. `sudo apt-get install python3-pip python3-dev libatlas-base-dev`
1. `pip3 install h5py pillow`
1. `pip3 install numpy`
1. `pip3 install tensorflow`
