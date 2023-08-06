
Connecting to an RGA
======================

Ethernet connection to a computer
----------------------------------

Serial connection to a Windows computer
-------------------------------------------

If the RGA is connected to a serial port of a Windows computer,

.. code-block:: python

    >>> import rga
    >>> rga1 = rga.RGA100('serial', 'COM3', 28800)
    >>> rga1.check_id()
    ('SRSRGA200', '19161', '0.24')
    >>>    


Serial connection to a Linux computer
-------------------------------------
    
If the RGA is connected to a serial port of a Linux system,

.. code-block:: python

    >>> from rga import RGA100
    >>>rga1 = RGA('serial', /dev/ttyUSB0', 28800)
    >>> rga1.check_id()
    ('SRSRGA200', '19161', '0.24')
    >>>    

If the RGA is connected to the Ethernet, regardless of computer systems,

.. code-block:: python

    >>> from rga import RGA120 as RGA
    >>> rga1 = RGA('tcpip', '172.25.40.39', 'admin', 'admin')
    >>> rga1.check_id()
    ('SRSRGA200', '19161', '0.24')
    >>>

If you get the next prompt '>>>', Congratulations. you are ready to control your SRS RGA with ``rga``.

