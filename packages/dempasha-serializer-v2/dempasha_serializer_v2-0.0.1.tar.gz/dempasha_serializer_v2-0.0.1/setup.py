from setuptools import setup, find_packages
import os

VERSION = '0.0.1'
DESCRIPTION = 'Serialzation tool'
LONG_DESCRIPTION = 'Serialzation tool'

# Setting up
setup(
    name="dempasha_serializer_v2",
    version=VERSION,
    author="Pavel Demeshkevich",
    author_email="<mail@neuralnine.com>",
    description=DESCRIPTION,
    long_description="my serializer",
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'serializer'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)