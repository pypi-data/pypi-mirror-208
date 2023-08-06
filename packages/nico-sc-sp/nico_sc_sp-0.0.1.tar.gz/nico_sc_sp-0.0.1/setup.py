from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Find covariation patterns between interacted cell types from spatial data'
LONG_DESCRIPTION = 'A package that perform cell type annotations on spatial transcriptomics data, find the niche interactions and covariation patterns between interacted cell types'

# Setting up
setup(
    name="nico_sc_sp",
    version=VERSION,
    author="Ankit Agrawal",
    author_email="<ankitplusplus@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['opencv-python'],
    keywords=['python', 'niche','spatial transcriptomics','single-cell rna sequencing','scRNAseq','nico'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
