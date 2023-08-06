
Scan operation
===============
``rga`` provides 4 different scan mode: analog scan, histogram scan,
multi mass scan (also called Pressure vs. Time scan), single mass scan (also called leak test).

Analog scan
------------
From the initial mass, final mass and steps-per-AMU values, scan data point are defined.

    * Use :meth:`rga.rga100.rga.RGA100.scan.get_mass_axis` to get the list of mass axis values for an analog scan.
    * Use :meth:`rga.rga100.rga.RGA100.scan.get_analog_scan` to perform and get a analog scan spectrum.

.. code-block:: python

    >>> from rga import RGA100 as RGA
    >>> rga1 = RGA('tcpip','172.25.40.39','admin','admin')
    >>> rga1.scan.set_parameters(20, 50, 5, 10) # Set the initial mass to 10, the final mass to 50,
    >>>                                         # scan speed to 1, and steps per AMU to 20.



Histogram scan
---------------

Multi mass scan
----------------

Single mass scan
-----------------


Mass lock
-----------

