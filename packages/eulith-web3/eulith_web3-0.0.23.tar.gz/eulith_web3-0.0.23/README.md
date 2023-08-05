# Welcome To Eulith Client
Please find our docs at https://docs.eulith.com

---

## Setup for Linux 22.04

~~~
sudo apt update -qq
sudo apt install -qq -y python3 python3-pip
pip3 install pyproject.toml
pip3 install web3
pip3 install pytest
export PATH=$PATH:$HOME/.local/bin   ; echo consider adding this to .bashrc
~~~

## Running tests

~~~
pytest
~~~

or if you use a different URL for where to find the eulith call server
~~~
EULITH_URL=http://192.168.244.44:7777/v0 pytest
~~~
