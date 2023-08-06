from setuptools import setup, find_packages

VERSION = '0.0.1-alpha'
DESCRIPTION = 'OakScript'
LONG_DESCRIPTION = 'TBD'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="oakscript",
    version=VERSION,
    author="houseofai",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'pinescript', 'tradingview'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)