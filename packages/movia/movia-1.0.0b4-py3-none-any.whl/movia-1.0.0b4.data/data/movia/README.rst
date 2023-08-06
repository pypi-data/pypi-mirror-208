.. rst syntax: https://deusyss.developpez.com/tutoriels/Python/SphinxDoc/
.. icons: https://specifications.freedesktop.org/icon-naming-spec/latest/ar01s04.html or https://www.pythonguis.com/faq/built-in-qicons-pyqt/
.. pyqtdoc: https://www.riverbankcomputing.com/static/Docs/PyQt6/

*****
Movia
*****

.. image:: https://github.com/pytest-dev/pytest/workflows/test/badge.svg
    :target: https://github.com/pytest-dev/pytest/actions?query=workflow%3Atest

.. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
    :target: https://github.com/PyCQA/pylint

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black


Decsription
-----------

This software proposes a graphic interface powered by pyqt6 (run ``movia-qt``).
The kernel is written in python and is easily integrated in other projects (module ``movia.core``).

This software is **light**, **fast** and **highly configurable** for the following reasons:

1. Based on ffmpeg, this software supports an incredible number of formats and codecs.
2. Thanks to operations on the assembly graph, it is able to perform nbr_opti optimization operations.
3. nbr_tests unit tests ensure an excelent kernel reliability.
4. Unlike other software that offers a timeline, this one allows you to edit an editing graph. This representation is more general and thus allows a greater flexibility.
5. A compiled version without graphical interface allows to allocate all the resources of the computer to the export.
6. This software generates at the time of the export a python code which can be edited. This offers an infinite number of possibilities!


Installation
------------

Movia has hard dependency on the pygraphviz library and on the ffmpeg package (version >= 4). You should install it first, please refer to the `pygraphviz installation guide <https://pygraphviz.github.io/documentation/stable/install.html>`_ and according to your Linux distribution, to the `FFmpeg download page <https://ffmpeg.org/download.html>`_.

In many cases, these commands should work:

.. code:: bash

    $ sudo apt install ffmpeg
    $ sudo apt install graphviz graphviz-dev

Although it is installed automatically, it is better to install **av** manually to avoid redundancy. Please refer to the `PyAv installation guide <https://pyav.org/docs/develop/overview/installation.html>`_.

In many cases, these commands should work:

.. code:: bash

    $ sudo apt install libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev
    $ pip install av --no-binary av

To install Movia using `PyPI <https://pypi.org/project/movia/>`_, run the following command:

.. code:: bash

    $ pip install movia[gui]

To install Movia from `Framagit <https://framagit.org/robinechuca/movia>`_ source, clone Movia using ``git`` and install it using ``pip``.:

.. code:: bash

    git clone https://framagit.org/robinechuca/movia.git
    cd movia/
    pip install -e ./[optional]

In a terminal, simply write the command ``movia-qt`` to launch the GUI and the command ``movia-test`` for launch the test banchmark.


What's new ?
------------

For the complete list of changes, refer to the `git commits <https://framagit.org/robinechuca/movia/-/network/main?ref_type=heads>`_.
