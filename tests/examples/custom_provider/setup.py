from setuptools import setup

setup(
    name="custom-provider-example",
    version="0.1.0",
    packages=["custom_provider"],
    install_requires=["secret-key-manager"],
)
