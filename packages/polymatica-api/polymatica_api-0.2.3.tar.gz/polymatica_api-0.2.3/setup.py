import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


requires = [
    "pydantic==1.10.7",
    "requests==2.29.0"
]

setuptools.setup(
    name="polymatica_api",
    version="0.2.3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.7',
    py_modules=["polymatica_api"],
    package_dir={'polymatica_api':'polymatica_api'},
    install_requires=requires
)
