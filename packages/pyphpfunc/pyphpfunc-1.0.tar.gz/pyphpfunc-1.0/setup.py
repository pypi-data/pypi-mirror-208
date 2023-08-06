import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyphpfunc",
    version="1.0",
    author="lgnove",
    author_email="lgynove@163.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),

    classifiers=[
    ],
    install_requires=[
    ],
    python_requires=">=3",
)