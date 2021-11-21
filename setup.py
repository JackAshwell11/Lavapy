import re
from setuptools import setup

with open("lavapy/__init__.py") as init:
    version = re.search(r'__version__ = "([\'0-9\'].[\'0-9\'].[\'0-9\'])"', init.read()).group(1)

with open("README.rst") as rdme:
    readme = rdme.read()

setup(
    name="Lavapy",
    version=version,
    author="Aspect1103",
    author_email="jack.ashwell1@gmail.com",
    license="MIT",
    url="https://github.com/Aspect1103/Lavapy",
    description="A powerful and robust Python library built from the ground up for interacting with Lavalink.",
    long_description=readme,
    packages=["lavapy"],
    python_requires=">=3.8",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ]
)
