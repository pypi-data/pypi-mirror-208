import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zmp",
    version="6.9",
    author="Zoe",
    author_email="zoe@zmp.lol",
    description="A few helpful python modules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZoeWithTheE/zm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)