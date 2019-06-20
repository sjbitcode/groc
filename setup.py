import pathlib
from setuptools import setup


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


# This call to setup() does all the work
setup(
    name="groc",
    version="0.0.1",
    description="Streamline your purchase history",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sjbitcode/groc",
    author="Sangeeta Jadoonanan",
    author_email="sjbitcode@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["groc"],
    include_package_data=True,
    install_requires=["click", "colorama", "ptable", "unidecode"],
    entry_points={
        "console_scripts": [
            "groc=groc.__main__:safe_entry_point",
        ]
    },
)
