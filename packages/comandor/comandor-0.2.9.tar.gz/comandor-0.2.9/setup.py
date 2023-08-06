from setuptools import setup

import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

setup(
    name='comandor',
    version='0.2.9',
    description='A Very Simple Script for Run your command!',
    long_description_content_type="text/markdown",
    long_description=long_description,
    url='https://github.com/NoobforAl/comandor',
    author='NoobforAl',
    author_email='FarshadSarmali@pm.me',
    license='MIT License',
    packages=['comandor'],
    keywords=["command line", "script"],
    install_requires=["pydantic >=1.10.5",
                      "tqdm >=4.65.0"],
    entry_points={
        "console_scripts": ['comandor = comandor.main:main']
    },

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
