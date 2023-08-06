# -*- coding: utf-8 -*-
import setuptools
import midoTrim

midoTrim.midifiles.midifiles.MidiFile().play()

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="midoTrim",
    version=midoTrim.version.__version__,
    author="Ole Martin Bjørndalen, bgArray",
    author_email="TriM-Organization@hotmail.com",
    description="Python的mid对象处理\n"
    "MIDI Objects for Python.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/TriM-Organization/mido",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: Chinese (Simplified)",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
