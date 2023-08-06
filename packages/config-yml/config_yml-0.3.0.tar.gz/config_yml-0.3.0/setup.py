""" Setup file """
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="config_yml",
    version="0.3.0",
    author="Ismael Raya",
    author_email="phornee@gmail.com",
    description="Utility modules for Class management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Phornee/config_yml",
    packages=setuptools.find_packages(),
    package_data={
        'tests': ['data/*.yml']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'PyYAML>=5.3.1'
    ],
    python_requires='>=3.6',
)