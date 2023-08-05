import pathlib
from setuptools import setup, find_packages
import pyNutFiles

# The text of the README file
ME_PATH = pathlib.Path(__file__).parent
README = (ME_PATH / "README.md").read_text()

# This call to setup() does all the work
setup(
    name    = "pynut-Files",
    version = pyNutFiles.__version__,
    description = "Function easing life :)",
    long_description = README,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Laurent-Tupin/pynut_Files",
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
    install_requires = ["pynut-tools==3.1.2", "openpyxl==3.1.0", "psutil==5.9.4",
                        "pywin32==305", "xlrd==2.0.1", "XlsxWriter==1.4.5",
                        "xlwings==0.29.1"]
    #entry_points={"console_scripts": ["EXEnameFile=FolderName.__main__:main"]},
)
