import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="weiming-demo",
    version="1.0.1",
    author="weiming.li",
    author_email="silang1225@126.com",
    description="Demo for parsing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://upload.pypi.org/legacy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
