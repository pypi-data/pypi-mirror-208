.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/csvsheet.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/csvsheet
    .. image:: https://readthedocs.org/projects/csvsheet/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://csvsheet.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/csvsheet/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/csvsheet
    .. image:: https://img.shields.io/conda/vn/conda-forge/csvsheet.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/csvsheet
    .. image:: https://pepy.tech/badge/csvsheet/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/csvsheet
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/csvsheet
.. image:: https://readthedocs.org/projects/csvsheet/badge/?version=latest
    :alt: ReadTheDocs
    :target: https://csvsheet.readthedocs.io/en/stable/
.. image:: https://img.shields.io/pypi/v/csvsheet.svg
    :alt: PyPI-Server
    :target: https://pypi.org/project/csvsheet/
.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

========
csvsheet
========


    Simple formula support for CSV


Description
===========

The aim of this project is to provide simple math capabilities to CSV files.
The capabilities are reduced to be able to use `python` formulas in a cell.
The formulas are evaluated using `eval`, so a basic sanitazion is done to avoid major risks, to do so, only `math` library can be used as well ass `int`, `float` and `+|-|*|\|(|)`.

Command line usage
==================

The command line requires a single compulsory arugment, the CSV fileto process::

    csvsheet <file.csv> -o <output.csv> -d <delimiter> -q <quotechar> -m <equation_delimiter> -v -vv
    csvsheet --help

The output file is optional, if not provided, the output will be printed to stdout.
The delimiter is also optional, if not provided, the default delimiter is `,`.
The quotechar is also optional, if not provided, the default quotechar is `"`.
The equation delimiter is also optional, if not provided, the default equation delimiter is `=`.

The `-v` and `-vv` flags are optional, they are used to increase the verbosity of the output.

Example
=======

The following example shows how to use the command line::

    csvsheet example.csv

If the contents of `example.csv` are::

    item,result
    Great,=1+2
    Not so great,=math.pow(2, 3)

The output will be::

    item,result
    Great,3
    Not so great,8.0


Python usage
============

The python usage is very simple, it is only required to import the `csvsheet` module and call the `run` function::

    import csvsheet

    csvsheet.run(["tests/test_a.csv"])

.. _pyscaffold-notes:

Making Changes & Contributing
=============================

This project uses `pre-commit`_, please make sure to install it before making any
changes::

    pip install pre-commit
    cd csvsheet
    pre-commit install

It is a good idea to update the hooks to the latest version::

    pre-commit autoupdate

Don't forget to tell your contributors to also install and use pre-commit.

.. _pre-commit: https://pre-commit.com/

Note
====

This project has been set up using PyScaffold 4.4.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
