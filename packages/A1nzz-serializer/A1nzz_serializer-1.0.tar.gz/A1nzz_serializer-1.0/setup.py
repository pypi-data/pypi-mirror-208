from setuptools import setup

setup(
    name="A1nzz_serializer",
    version="1.0",
    description="module for python (de)serialization in Json and Xml",
    url="https://github.com/A1nzz/Python-Labs/tree/Lab3",
    author="Mamchenko Kirill",
    author_email="kmamcenko@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["Serializers"],
    include_package_data=True,
    install_requires=["regex"]
)
