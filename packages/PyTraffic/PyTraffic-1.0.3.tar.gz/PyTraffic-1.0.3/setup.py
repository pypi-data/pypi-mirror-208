# PyTraffic - Setup.py

''' This is the 'setup.py' file. '''

# Imports
from setuptools import setup, find_packages

# README.md
with open("README.md") as readme_file:
    README = readme_file.read()

# Setup Arguements
setup_args = dict (
    name="PyTraffic",
    version="1.0.3",
    description="PyTraffic is a Python module to work on traffic-related functions and use cases.",
    long_description_content_type="text/markdown",
    long_description=README,
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    author="Aniketh Chavare",
    author_email="anikethchavare@outlook.com",
    keywords=["Traffic", "Traffic Density", "License Plates", "Speed", "Speed Calculation"],
    url="https://github.com/Anikethc/PyTraffic",
    download_url="https://pypi.org/project/PyTraffic"
)

# Install Requires
install_requires = ["opencv-python", "imutils", "numpy", "pytesseract"]

# Run the Setup File
if __name__ == "__main__":
    setup(**setup_args, install_requires=install_requires)