import pathlib
from setuptools import setup, find_packages, find_namespace_packages
import py2Nut  #, pynut_1tools

# The text of the README file
ME_PATH = pathlib.Path(__file__).parent
README = (ME_PATH / "README.md").read_text()
NAME = "py2nut"
VERSION = py2Nut.__version__


# This call to setup() does all the work
setup(
    name = NAME,
    version = VERSION,
    description = "This Library allows you to make Misc operations in various domain",
    long_description = README,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Laurent-Tupin/py2nut",
    author = "Laurent Tupin",
    author_email = "laurent.tupinn@gmail.com",
    license = "Copyright 2022-2035",
    classifiers=[
        "License :: Free For Home Use",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    # packages = find_packages(exclude = ("test",) ), 
    # packages = find_packages(include=["py2Nut","pynut_1tools", "pyNutTools"] ), 
    # include_package_data = True,
    packages = find_namespace_packages( where = '.', exclude = [ '*test*', '*pynut_1tools/setup.py*', '*pynut_2api/setup.py*',
                                                                 '*pynut_2files/setup.py*','*pynut_3db/setup.py*',
                                                                 '*pynut_3email/setup.py*', '*pynut_3ftp/setup.py*'] ),
    install_requires = ["datefinder==0.7.3"]
    # ,entry_points={"console_scripts": ["EXEnameFile=FolderName.__main__:main"]}
)
