from setuptools import find_packages, setup
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="mongo_to_som",
    packages=["mongo_to_som"],
    include_package_data=True,
    version='1.0.8',
    description='Library to create Self-Organizing Map from MongoDB collection',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Tomáš Peregrín',
    author_email="djtoso@gmail.com",
    license='MIT',
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'pandas',
        'scikit-learn',
        'pymongo',
        'numpy',
        'scipy',
        'matplotlib'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)