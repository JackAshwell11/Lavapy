import os
import re
from setuptools import setup

with open("lavapy/__init__.py") as init:
    version = re.search(r'__version__ = "([\'0-9\'].[\'0-9\'].[\'0-9\'])"', init.read()).group(1)

with open("README.rst") as rdme:
    readme = rdme.read()

with open("requirements.txt") as rqmnts:
    requirements = rqmnts.read().splitlines()

if os.getenv("READTHEDOCS") == "True":
    with open("docs/requirementsRTD.txt") as rqmnts:
        requirements.extend(rqmnts.read().splitlines())

setup(
    name="Lavapy",
    version=version,
    description="A powerful and robust Python library built from the ground up for interacting with Lavalink.",
    long_description=readme,
    author="Aspect1103",
    author_email="jack.ashwell1@gmail.com",
    license="MIT",
    url="https://github.com/Aspect1103/Lavapy",
    packages=["lavapy", "lavapy.ext.spotify"],
    keywords=["lavapy", "lavalink", "discord.py"],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed"
    ]
)
