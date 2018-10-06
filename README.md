## Setup on Raspberry Pi

1. `sudo apt-get update`
1. `sudo apt-get install python-dev python-pip`
1. `sudo pip install pipenv`
1. `curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash`

## References
1. Pinout for RaspberryPi: http://pinout.xyz

## Running under systemd
1. Copy service file `sudo cp robotwedding.service /lib/systemd/system/`
1. Test with `sudo systemctl start robotwedding.service` and `sudo systemctl stop robotwedding.service`.
1. Enable at boot with `sudo systemctl enable robotwedding.service`
