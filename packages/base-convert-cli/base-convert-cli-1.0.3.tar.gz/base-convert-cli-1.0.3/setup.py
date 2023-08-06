from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="base-convert-cli",
    description="A CLI tool that converts numbers between bases.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="1.0.3",
    url="https://github.com/Kevinpgalligan/bs",
    author="Kevin Galligan",
    author_email="galligankevinp@gmail.com",
    scripts=["scripts/bs"],
    packages=find_packages("src"),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[]
)
