from setuptools import setup

setup(
    name="MySerializatorOfXmlAndJson",
    version="0.1.1",
    description="Library for serialization",
    author="Ilya Danilenko",
    author_email="ilyadanilenko2003@mail.ru",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["serializers"],
    include_package_data=True,
    install_requires=["regex"]
)