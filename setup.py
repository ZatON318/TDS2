from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tds2",
    version="0.2.0",
    author="ZatOFF",
    author_email="zaton318@gmail.com",
    description="lib for file management with telegram api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZatON318/TDS2",
    packages=find_packages(),
    install_requires=[
        'telethon',
        'tqdm',
        'python-dotenv',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)