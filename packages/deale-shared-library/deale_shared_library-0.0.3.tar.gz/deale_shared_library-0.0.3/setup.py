from setuptools import find_packages, setup

setup(
    name="deale_shared_library",
    version="0.0.3",
    packages=find_packages(),
    description="A shared library for Deale microservices",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        # List your library dependencies here
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)
