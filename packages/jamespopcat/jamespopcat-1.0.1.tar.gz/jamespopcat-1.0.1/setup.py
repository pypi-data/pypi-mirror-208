from setuptools import setup, find_packages

setup(
    name='jamespopcat',
    version='1.0.1',
    description='Auto clicker Popcat',
    author='CTRCRK',
    author_email='ctrcrk.id@gmail.com',
    py_modules=['jamespopcat'], 
    packages=find_packages(),
    install_requires=[
        'selenium',
        'psutil',
    ],
)
