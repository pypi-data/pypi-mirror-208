#######
RaGraph
#######

RaGraph is a package to create, manipulate, and analyze graphs consisting of nodes and
edges. Nodes usually represent (hierarchies of) objects and edges the dependencies or
relationships between them.

These graphs, or networks if you will, lend themselves well to applied analyses like
clustering and sequencing, as well as analyses involving the calculation of various
insightful metrics.


**********
Quickstart
**********

Installation
============

RaGraph can be installed using ``pip install ragraph[all]`` for any Python version >=3.9. Or,
for Poetry managed projects, use ``poetry add ragraph -E all`` to add it as a dependency.


Using RaGraph
=============

RaGraph's primary use is working with Graph objects that contain Nodes and Eges between
Nodes. See the `usage documentation <https://ragraph.ratio-case.nl/usage/index.html>`_
for more info!

***************
Developer guide
***************

Python packaging information
============================

This project is packaged using `poetry <https://python-poetry.org/>`_. Packaging
information as well as dependencies are stored in `pyproject.toml <./pyproject.toml>`_.

Installing the project and its development dependencies can be done using ``poetry install -E all``.

Versioning
==========

This project uses `semantic versioning <https://semver.org>`_. Version increments are
checked using `Raver <https://raver.ratio-case.nl>`_.

Changelog
=========

Changelog format as described by https://keepachangelog.com/ has been adopted and can be reviewed `on this page <https://ragraph.ratio-case.nl/changelog.html>`.

Tests
=====

Tests can be run using ``poetry run pytest``.

Linting
=======

Linting config is included in `pyproject.toml <./pyproject.toml>`_ for both Black and Ruff.
