"""
setup file for django-nepali package

- Building a package

    pip install build
    python -m build


- Publishing a package
You must have twine installed in your system. `pip install twine`

    python setup.py sdist bdist_wheel
    twine upload dist/*

"""
import os
import sys
import setuptools

long_description = "# django-nepali"


if sys.argv[-1] == "publish":
    if os.system("pip3 freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("rm -rf dist")
    os.system("python3 setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()


setuptools.setup(
    name="django-nepali",
    version="0.0.0",
    author="opensource-nepal",
    author_email="aj3sshh@gmail.com",
    description="Django package for supporting nepali package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "django",
        "nepali date conversion",
        "convert date",
        "nepali date time",
        "python convert date",
        "parse nepali date time",
    ],
    url="https://github.com/opensource-nepal/django-nepali",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
