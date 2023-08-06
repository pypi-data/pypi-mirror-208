from setuptools import setup, find_packages

setup(
    name='dexchange-sms',
    version='1.0.2',
    author='DENVER',
    author_email='denver@denver-dev.com',
    description='PY package for DEXCHANGE SMS API',
    packages=find_packages(),
    install_requires=['requests'], 
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://dexchange-sms.com',
    project_urls={
        'Documentation': 'https://documenter.getpostman.com/view/23992877/2s93ebTrC1#',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],

)
