import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ib110hw",
    version="0.1.7",
    author="Martin Pilát",
    author_email="8pilatmartin8@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pynput",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    url="https://github.com/pilatmartin/ib110hw",
)
