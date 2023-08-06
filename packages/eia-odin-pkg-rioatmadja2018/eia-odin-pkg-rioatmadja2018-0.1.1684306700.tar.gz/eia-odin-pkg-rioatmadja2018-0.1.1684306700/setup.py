"""Setup file for building/deploying this wheel."""
import os
import time

from setuptools import find_packages, setup

VERSION_BRANCH = ""
BITBUCKET_BRANCH: str = os.getenv("BITBUCKET_BRANCH", "") 
if BITBUCKET_BRANCH and BITBUCKET_BRANCH != "master":
    VERSION_BRANCH = sum([ord(x) for x in BITBUCKET_BRANCH])

# Gather requirements from requirements.txt.  It's
# important to put all dependencies in requirements.txt rather
# then here.
#
# We're doing this because SSL v3 isn't supported by the
# setup tools dependency_links option.  Our pypi repo uses
# SSL v3 so we need to use pip (which does support SSL v3)
# to install dependencies (using requirements.txt)
install_requires = []
with open('requirements.txt') as fp: 
    for line in fp: 
        if not line.startswith('--') and not line.startswith('#'):
            install_requires.append(line)

# The actual call to setup tools
setup(
    name='eia-odin-pkg-rioatmadja2018',
    version=f'0.1.{VERSION_BRANCH}{int(time.time())}',
    description='Python Wheels to interact with the EIA APIs',
    long_description=open('README.md', 'r').read(),
    author='Rio Atmadja',
    author_email='rioatmadja2018@gmail.com',
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],  
    zip_safe=True,
    python_requires='>=3.8'
)
