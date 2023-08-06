from setuptools import setup, find_packages

setup(
    name="Json-And-Xml-Serializer-Eugene",
    version="0.1.0",
    description="Library for class and function serialization",
    author="Evgeny Kuznetsov",
    author_email="jenakuz2003@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["serializer.src"],
    include_package_data=True
)
