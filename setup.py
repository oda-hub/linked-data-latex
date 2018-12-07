import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "rich-draft-templating",
    version = "0.1.1",
    author = "Volodymyr Savchenko",
    author_email = "contact@volodymyrsavchenko.com",
    description = (""),
    license = "BSD",
    packages=['ddpaper'],
    long_description=read('README.md'),
    entry_points = {
        'console_scripts': [
            'ddpaper=ddpaper.generate:main'
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
