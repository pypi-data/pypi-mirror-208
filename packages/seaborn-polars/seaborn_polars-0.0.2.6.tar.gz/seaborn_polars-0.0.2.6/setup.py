import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="seaborn_polars",                           # This is the name of the package
    version="0.0.2.6",                                 # The initial release version
    author="Pavel Cherepanskiy",                     # Full name of the author
    description="Wrapper for plotting with seaborn using Polars dataframes and lazyframes",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.8',                # Minimum version requirement of the package
    py_modules=["seaborn_polars"],             # Name of the python package
    package_dir={'':'seaborn_polars/src'},     # Directory of the source code of the package
    install_requires=[]          # Install other dependencies if any
)