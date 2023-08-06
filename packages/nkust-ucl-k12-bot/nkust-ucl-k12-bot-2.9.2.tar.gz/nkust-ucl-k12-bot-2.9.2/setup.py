import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="nkust-ucl-k12-bot",
    version="2.9.2",
    author="Ethan Cheng",
    author_email="asdewq45445@gmail.com",
    description="一個用於k12的bot包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xinbow99/k12-telegram",
    packages=setuptools.find_packages(),
    install_requires=[
        
        "paho-mqtt==1.6.1",
        "PyYAML==6.0",
        "requests==2.28.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)