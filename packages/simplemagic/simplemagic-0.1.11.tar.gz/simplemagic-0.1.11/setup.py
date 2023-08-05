import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires = [x.strip() for x in fobj.readlines() if x.strip()]

setup(
    name="simplemagic",
    version="0.1.11",
    description="Simple file magic. We try to get file's mimetype using 'file-magic', 'command file' and 'puremagic'. On linux we need system package 'file-libs' which mostly already installed. On MacOS we need system package 'libimage' which can be installed by 'brew install libmagic'. On windows we need file command which can be install by 'pacman -S file' within msys2. If system package missing, we try to get the file's mimetype using 'puremagic' which is write in pure python without any extra depends.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="zencore",
    author_email="dobetter@zencore.cn",
    license="MIT",
    license_files=("LICENSE",),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["libmagic", "file-magic", "file"],
    install_requires=requires,
    packages=find_packages("."),
    entry_points={
        "console_scripts": [
            "filemagic = simplemagic.cli:main",
        ]
    },
)
