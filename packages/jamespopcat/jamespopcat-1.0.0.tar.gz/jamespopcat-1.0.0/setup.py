from setuptools import setup, find_packages

setup(
    name='jamespopcat',
    version='1.0.0',
    description='Auto clicker Popcat',
    author='CTRCRK',
    author_email='ctrcrk.id@gmail.com',
    packages=find_packages(),
    install_requires=[
        'selenium',
        'psutil',
    ],
)
