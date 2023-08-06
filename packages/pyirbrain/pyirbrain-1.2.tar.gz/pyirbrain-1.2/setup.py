from setuptools import setup, find_packages

setup(
    name = "pyirbrain",
    version = "1.2", 
    description = "Library for IR-Brain Products",
    author = "IR-Brain",
    author_email = "ceo@ir-brain.com",
    url = "http://www.ir-brain.com",
    packages = ['pyirbrain', 
        ],
    install_requires = [
        'pyserial>=3.4',
        'pynput>=1.7.3',
        ],
)
