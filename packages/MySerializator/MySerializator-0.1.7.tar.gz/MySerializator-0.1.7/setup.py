from setuptools import setup

setup(
    name="MySerializator",
    version="0.1.7",
    description="My Library for serialization",
    author="Ilya Danilenko",
    author_email="ilyadanilenko2003@mail.ru",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["serializers"],
    include_package_data=True,
)