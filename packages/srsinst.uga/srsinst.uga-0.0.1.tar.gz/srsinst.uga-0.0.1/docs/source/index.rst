.. SRS RGA documentation master file, created by
   sphinx-quickstart on Sun Oct  9 16:07:41 2022.

.. _overview:

``rga`` documentation
===================================
``rga`` is a `Python 3 package <https://realpython.com/python-modules-packages/>`_ 
to control and acquire data from 
`Stanford Research Systems (SRS) Residual Gas Analyzer (RGA)
<https://thinksrs.com/products/rga.html>`_ over **serial** and **Ethernet communication**.
 
**SRS RGA** is a `residual gas analyzer <https://en.wikipedia.org/wiki/Residual_gas_analyzer>`_ 
using `quadrupole mass filter <https://en.wikipedia.org/wiki/Quadrupole_mass_analyzer>`_ 
running in a vacuum system. Any measurement instruments running in vacuum require great attention
to operate without damaging them or the pumping system. It is important to familiar yourself
to **SRS RGA** before using ``rga`` to control an **SRS RGA**. If you are new to **SRS RGA**, here is
the  `user's manual <https://thinksrs.com/downloads/pdfs/manuals/RGAm.pdf>`_ for your reading pleasure.


.. toctree::
   :maxdepth: 2

   installation
   connection
   basic_operation
   scan_operation
   rga120_operation
   
   uga100

   license

Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
