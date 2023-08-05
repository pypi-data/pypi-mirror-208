import pathlib
from setuptools import setup, find_packages
import pyNutTools

# The text of the README file
ME_PATH = pathlib.Path(__file__).parent
README = (ME_PATH / "README.md").read_text()

# This call to setup() does all the work
setup(
    name    = "pynut-tools",
    version = pyNutTools.__version__,
    description = "Function easing life :)",
    long_description = README,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Laurent-Tupin/pynut_tools",
    author = "Laurent Tupin",
    author_email = "laurent.tupinn@gmail.com",
    license = "Copyright 2022-2035",
    classifiers=[
        "License :: Free For Home Use",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages = find_packages(exclude = ("test",)),
    include_package_data = True,
    install_requires = ["pandas==1.5.3", "datefinder==0.7.3"]
    #entry_points={"console_scripts": ["EXEnameFile=FolderName.__main__:main"]},
)
