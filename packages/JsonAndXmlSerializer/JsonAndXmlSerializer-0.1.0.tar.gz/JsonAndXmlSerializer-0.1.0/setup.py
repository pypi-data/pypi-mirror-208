from setuptools import setup, find_packages

setup(
    name="JsonAndXmlSerializer",
    version="0.1.0",
    description="Library for class and function serialization",
    author="Evgeny Kuznetsov",
    author_email="jenakuz2003@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["Serializer"],
    include_package_data=True,
    install_requires=["regex"]
)
