import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "iosense_connect",
    version = "2.1.6",
    author = "Faclon-Labs",
    author_email = "reachus@faclon.com",
    description = "iosense connect library",
    packages = ["iosense_connect"],
    long_description = long_description,
    long_description_content_type = "text/markdown",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
