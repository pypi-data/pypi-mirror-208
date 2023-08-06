# TEMPCF: Cleaning and Filtering for Ground Temperature Data

This package provides a graphical user interface for viewing, flagging, and cleaning ground temperature data for permafrost applications. It is designed to work with a variety of different input data types including data loggers, and databases. It uses read / write functionality provided by the [teaspoon](https://gitlab.com/permafrostnet/teaspoon) package ([Brown, 2022](https://joss.theoj.org/papers/10.21105/joss.04704)).

For a full description of the package, including some examples, please see the [documentation pages](https://permafrostnet.gitlab.io/permafrost-tempcf/).


# How to get tempcf
There are a few ways to get tempcf running on your computer.

## Install from pip

You can install tempcf with pip:
```cmd
pip install tempcf
```

Then you can run it from the command line with:
```cmd
tempcf
```

## Running pre-compiled executables

As an alternative to command-line installation, its possible to download the latest files from the [Releases](https://gitlab.com/permafrostnet/permafrost-tempcf/-/releases) page of the GitLab repository. This requires no coding experience whatsoever, but only works on Windows and Linux at the moment. These also won't be the most up-to-date versions.

If you are familiar with python and would rather run tempf from the source code, follow the instructions below. This is the preferred option if you intend to contribute, or if you want to make any modifications.

## Install from source

### Step 1: Download the files

```
git clone https://gitlab.com/permafrostnet/permafrost-tempcf
```

### Step 2: Create a virtual environment

This makes sure that the python packages that get installed don't conflict with other python packages you might have installed.
On Mac or Linux, make sure to replace '\' with '/' in the last line.

```cmd
cd permafrost-tempcf
python -m venv env
.\env\Scripts\activate 
```

### Step 3: Install tempcf

These commands will install the required dependencies, and launch tempcf

```cmd
python setup.py install
cd tempcf
python main.py
```


