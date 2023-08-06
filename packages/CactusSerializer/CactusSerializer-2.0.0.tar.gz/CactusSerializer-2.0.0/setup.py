from setuptools import setup, find_packages

setup(
    name="CactusSerializer",
    version="2.0.0",
    description="module for serialization/deserialization(JSON, XML)",
    url="https://github.com/Antilevskaya-Ksenia-153501/Python-labs/tree/lab3",
    author="Ksenia Antilevskaya",
    author_email="antikevkun@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["Serializer"],
    include_package_data=True
)
