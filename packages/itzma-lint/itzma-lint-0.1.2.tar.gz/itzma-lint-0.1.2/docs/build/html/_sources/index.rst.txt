.. itzma-lint documentation master file, created by
   sphinx-quickstart on Thu May 11 23:34:42 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to itzma-lint's documentation!
======================================

Description
======================

.. include:: ../../README.md
   :parser: myst_parser.sphinx_

Documentation
======================
.. automodule:: checks
      :members:
.. autoclass:: checks.LocalImportsNotAllowed
      :members:
.. autoclass:: checks.UnconventionalFunctionNamesNotAllowed
      :members:
.. autoclass:: checks.UnconventionalClassNamesNotAllowed
      :members:
.. autoclass:: checks.UnconventionalVariableNamesNotAllowed
      :members:

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Examples
======================

To check the formatting of file_sample.py, run the following command:

   :code: flake8 file_sample.py

To focus on CamelCase(IMC) or snake_case(IMS) add tag --select

   :code: flake8 file_sample.py ---select=IMC

or

   :code: flake8 file_sample.py ---select=IMS

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
