from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='jamespopcat',
    version='1.0.3',
    description='Auto clicker Popcat',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='CTRCRK',
    author_email='ctrcrk.id@gmail.com',
    py_modules=['jamespopcat'], 
    packages=find_packages(),
    install_requires=[
        'selenium',
        'psutil',
    ],
    license='Apache License 2.0'
)
