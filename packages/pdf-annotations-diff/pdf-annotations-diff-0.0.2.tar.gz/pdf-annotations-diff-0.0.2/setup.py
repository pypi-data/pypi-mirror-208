from setuptools import setup
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pdf-annotations-diff",
    version="0.0.2",
    description="A tool to compare PDF annotations",
    long_description=long_description,
    long_description_content_type="text/markdown",  # This is important!
    author="Sameer Ahuja",
    author_email="pdf-annotations-diff@sameerahuja.com",
    url="https://github.com/sam33r/pdf-annotations-diff",
    py_modules=["pdf_annotations_diff"],
    install_requires=[
        "PyMuPDF",
    ],
    entry_points={
        "console_scripts": [
            "pdf-annotations-diff=pdf_annotations_diff:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
