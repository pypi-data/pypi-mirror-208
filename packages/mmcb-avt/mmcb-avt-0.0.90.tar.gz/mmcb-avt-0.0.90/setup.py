from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="mmcb-avt",
    version="0.0.90",
    author="Alan Taylor, Manex Ormazabal",
    author_email="avt@hep.ph.liv.ac.uk",
    maintainer="Alan Taylor",
    maintainer_email="avt@hep.ph.liv.ac.uk",
    description="ATLAS ITK Pixels Multi-Module Cycling Box environmental monitoring/control.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.ph.liv.ac.uk/avt/atlas-itk-pmmcb",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "zmq",
        "pyserial>=3.5",
        "smbus",
        "tables",
        "Adafruit-Blinka",
        "adafruit-circuitpython-ads1x15",
        "adafruit-circuitpython-bme680",
        "adafruit-circuitpython-pcf8591",
        "adafruit-circuitpython-shtc3",
        "sparkfun-qwiic-tca9548a",
        "yoctopuce",
    ],
    entry_points={
        "console_scripts": [
            "dat2plot = mmcb.dat2plot:main",
            "dat2root = mmcb.dat2root:main",
            "detect = mmcb.detect:main",
            "dmm = mmcb.dmm:main",
            "iv = mmcb.iv:main",
            "liveplot = mmcb.liveplot:main",
            "log2dat = mmcb.log2dat:main",
            "peltier = mmcb.peltier:main",
            "psuset = mmcb.psuset:main",
            "psustat = mmcb.psustat:main",
            "sense = mmcb.sense:main",
            "ult80 = mmcb.ult80:main",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
    ],
)
