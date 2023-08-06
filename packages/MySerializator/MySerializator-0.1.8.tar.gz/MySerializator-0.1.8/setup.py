from setuptools import setup, find_packages

setup(
    name="MySerializator",
    version="0.1.8",
    description="My Library for serialization",
    author="Ilya Danilenko",
    author_email="ilyadanilenko2003@mail.ru",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(),
    include_package_data=True,
)