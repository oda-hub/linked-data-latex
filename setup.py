import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "rich-draft-templating",
    version = "0.1.1",
    author = "V.S.",
    #author_email = "andrewjcarter@gmail.com",
    ##description = (""),
    license = "BSD",
    packages=['ddpaper'],
    #long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)