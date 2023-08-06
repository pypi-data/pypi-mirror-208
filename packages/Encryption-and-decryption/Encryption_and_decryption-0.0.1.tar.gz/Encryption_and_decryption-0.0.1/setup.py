from setuptools import setup, find_packages
import os

requirements = os.popen("/usr/local/bin/pipreqs main --print").read().splitlines()

setup(
    name='Encryption_and_decryption',
    version='0.0.1',
    author='Sridhar',
    author_email='dcsvsridhar@gmail.com',
    description="Encryption_and_decryption Methods in Python",
    packages=find_packages(),
    url='https://git.selfmade.ninja/SRIDHARDSCV/encryption_and_decryption',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'Endecoder=src.app:main',
        ],
    },
)
