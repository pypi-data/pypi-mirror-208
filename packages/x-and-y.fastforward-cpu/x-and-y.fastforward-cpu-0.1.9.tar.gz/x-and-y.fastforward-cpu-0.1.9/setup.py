import os
# read the contents of your README file
from pathlib import Path

import pkg_resources
from setuptools import find_packages, setup

long_description = Path(__file__).with_name("README.md").read_text()

setup(
    name='x-and-y.fastforward-cpu',
    packages=find_packages(exclude=("__tests__","fastforward.__tests__")),
    version='0.1.9',
    license='Apache Software License',
    description='Fastforward is an inference engine for efficient AI models.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='x-and-y',
    author_email='christian.weber@leftshift.one',
    url='https://github.com/c7nw3r/fastforward',
    download_url='https://github.com/c7nw3r/fastforward/archive/refs/tags/v0.1.9.tar.gz',
    keywords=['onnx-engine', 'machine-learning', 'artificial-intelligence'],
    setup_requires=['setuptools_scm'],
    include_package_data=True,
    install_requires=[
        str(r)
        for r in pkg_resources.parse_requirements(
            open(os.path.join(os.path.dirname(__file__), "requirements.txt"))
        )
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
