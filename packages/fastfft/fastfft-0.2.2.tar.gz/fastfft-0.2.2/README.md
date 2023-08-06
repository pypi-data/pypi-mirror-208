# Fast fourier transform algorithm implementation
## Installation
Python 3.8.15 required for OS X
Python 3.5 required for Linux
### OS X
Simply, run
````shell
pip install fastfft
````
### Linux
Install some additional packages
````shell
sudo apt-get install build-essential
sudo apt install python-dev gcc
sudo apt-get install python3-dev
````
And install the package
````shell
pip install fastfft
````
## Usage
Just import and use
````python
from fastfft.fft import fft2, ifft2
matrix = [
    [1.0, 2.0],
    [3.0, 4.0],
]
image = fft2(matrix)
original = ifft2(image)
````
