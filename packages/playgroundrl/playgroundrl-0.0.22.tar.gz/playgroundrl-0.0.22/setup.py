from setuptools import setup

setup(
   name='playgroundrl',
   version='0.0.22',
   author='Rayan Krishnan',
   packages=['playgroundrl'],
   package_dir={'':'src'},
   scripts=[],
   url='http://pypi.python.org/pypi/playgroundrl/',
   description='Python SDK for Playground RL',
   # long_description=open('README.txt').read(),
   install_requires=[
        'python-socketio==5.6.0',
        'attrs==22.2.0',
        'cattrs==22.2.0',
   ],
)
