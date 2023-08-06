from setuptools import setup, find_packages
import pynterface

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="pynterface",
    version=pynterface.__version__,
    author=pynterface.__author__,
    author_email='singhvi.vivaan@gmail.com',
    description='Terminal-Based Printing Tools!',
    long_description=description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.8',
    include_package_data=True,
    project_urls={
        "Documentation": "https://pynterface.readthedocs.io/en/latest/"
    }
)