from setuptools import Extension, dist, find_packages, setup
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='quickpanda',
    version="0.0.4",
    description='quickpanda',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='data analysis',
    url='https://github.com/yasuo626/QuickPanda',
    author='aidroid',
    author_email='yasuo626.com@gmail.com',
    # packages=find_packages(),

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

    python_requires = '>=3.6',
    # install_requires=[
    #     'pandas',
    #     'sklearn',
    #     'numpy',
    # ],





    # entry_points={
    #     'console_scripts': [
    #         'foo = foo.main:main'
    #     ]
    # },
    # scripts=['bin/foo.sh', 'bar.py'],


)
