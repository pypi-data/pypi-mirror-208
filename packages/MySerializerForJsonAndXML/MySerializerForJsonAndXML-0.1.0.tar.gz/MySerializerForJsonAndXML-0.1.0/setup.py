from setuptools import setup

setup(
    name="MySerializerForJsonAndXML",
    version="0.1.0",
    description="Demo library",
    author="Teplyakov Arseny",
    author_email="teplyakovarseni@mail.ru",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["Serializators"],
    include_package_data=True,
    install_requires=["regex"]
)
