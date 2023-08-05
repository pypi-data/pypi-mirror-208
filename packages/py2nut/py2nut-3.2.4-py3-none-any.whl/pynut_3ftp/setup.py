import pathlib
from setuptools import setup, find_packages
import pyNutFtp

# The text of the README file
ME_PATH = pathlib.Path(__file__).parent
README = (ME_PATH / "README.md").read_text()
NAME = "pynut-ftp"
VERSION = pyNutFtp.__version__

# This call to setup() does all the work
setup(
    name    = NAME,
    version = VERSION,
    description = "Function easing life :)",
    long_description = README,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Laurent-Tupin/pynut_DB",
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
    install_requires = ["pynut-Files==3.2.2", "paramiko==3.0.0", "pysftp==0.2.9"]
    #entry_points={"console_scripts": ["EXEnameFile=FolderName.__main__:main"]},
)
