from setuptools import setup, find_packages

setup(
    name='dexchange-sms',
    version='1.0.0',
    author='DENVER',
    author_email='denver@denver-dev.com',
    description='PY package for DEXCHANGE SMS API',
    packages=find_packages(),
    install_requires=['requests'], 
)
