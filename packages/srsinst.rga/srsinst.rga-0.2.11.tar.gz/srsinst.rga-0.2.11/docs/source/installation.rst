
.. _top_of_installation:

Installation
===============

To use ``srsinst.rga``, you need to `install Python <install-python_>`_ on your computer.
Python package installer, `pip`_ is available, after Python is installed.

Once you have a working `pip`_, install ``srsinst.rga`` from the command line.

.. code-block:: 

    python -m pip install srsinst.rga


When you start Python from the command line, the '>>>' prompt is waiting for your input.

.. code-block:: python

    C:\rga>python
    C:\PyPI\rga>C:\Users\ckim\AppData\Local\Programs\Python\Python38\python.exe    
    Python 3.8.3 (tags/v3.8.3:6f8c832, May 13 2020, 22:37:02) [MSC v.1924 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

Import ``srsinst.rga``, and check for its version. If you see the version number,
software installation is done correctly. 

.. code-block:: python

    C:\rga>python.exe
    Python 3.8.3 (tags/v3.8.3:6f8c832, May 13 2020, 22:37:02) [MSC v.1924 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>>
    >>> import stsinst.rga as rga
    >>> rga.__version__
    '0.2.0'
    >>>
 

.. _install-python : https://realpython.com/installing-python/
.. _pip: https://realpython.com/what-is-pip/