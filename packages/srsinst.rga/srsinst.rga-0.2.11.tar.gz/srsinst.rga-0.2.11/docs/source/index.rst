.. SRS RGA documentation master file, created by
   sphinx-quickstart on Sun Oct  9 16:07:41 2022.

.. _overview:

``srsinst.rga`` documentation
===================================
``srsinst.rga`` is a `Python 3 package <package_>`_ to control and acquire data with
`Stanford Research Systems (SRS) Residual Gas Analyzer (RGA) <rga100_>`_
using `srsgui`_  as a graphic user interface (GUI).

    ..  image:: _static/image/derived-pvst-plot-screenshot.png
        :width: 500pt
        :target: `overview`_   
 
**SRS RGA** is a `residual gas analyzer <rga_>`_ using `quadrupole mass filter <qmf_>`_
running in a vacuum system. Any measurement instruments running in vacuum require great attention
to operate without damaging them or the pumping system. It is important to familiar yourself
to **SRS RGA** before using ``srsinst.rga`` to control an **SRS RGA**. If you are new to **SRS RGA**, here is
the  `user's manual <manual_>`_ for your reading pleasure.


.. toctree::
   :maxdepth: 4

   installation
   connection
   basic_operation
   scan_operation
   
   srsinst.rga

   license

Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _srsgui: https://pypi.org/project/srsgui/
.. _package: https://realpython.com/python-modules-packages/
.. _rga100: https://thinksrs.com/products/rga.html
.. _rga: https://en.wikipedia.org/wiki/Residual_gas_analyzer
.. _qmf: https://en.wikipedia.org/wiki/Quadrupole_mass_analyzer
.. _manual: https://thinksrs.com/downloads/pdfs/manuals/RGAm.pdf