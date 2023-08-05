# PySciMath - Setup.py

''' This is the 'setup.py' file. '''

# Imports
from setuptools import setup, find_packages

# README.md
with open("README.md") as readme_file:
    README = readme_file.read()

# Setup Arguements
setup_args = dict (
    name="PySciMath",
    version="1.5.0",
    description="PySciMath is a general-purpose Python module to work on calculations and solve mathmematical and scientific problems.",
    long_description_content_type="text/markdown",
    long_description=README,
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    author="Aniketh Chavare",
    author_email="anikethchavare@outlook.com",
    keywords=["Math", "Calculations"],
    url="https://github.com/Anikethc/PySciMath",
    download_url="https://pypi.org/project/pyscimath"
)

# Run the Setup File
if __name__ == "__main__":
    setup(**setup_args)