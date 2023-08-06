
Basic Operation
================
SRS RGA is a quadrupole mass mass spectrometer. It consists of the ionizer that produce ions,
the quadrupole mass filter that selects ions of a specific mass-to-charge ratio (m/z),
and the ion detector that measures the intensity of selected ions. Refer to the
manual <https://thinksrs.com/downloads/pdfs/manuals/RGAm.pdf>`_ chapter 3.

Setup ionizer parameters
-------------------------
SRS RGA generates positive ions from residual gas in a vacuum system using
`electron ionization method <https://en.wikipedia.org/wiki/Electron_ionization>`_.
You can adjust the electron energy, ion energy, focus plate voltage to control ion generation.
The filament emission current is controlled separtedly in the following section.

    * Use :meth:`rga.rga100.components.Ionizer.set_parameters` to set ionizer parameters.
    * Use :meth:`rga.rga100.components.Ionizer.get_parameters` to get a
      `tuple <https://realpython.com/python-lists-tuples/#python-tuples>`_ of 
      (electron_energy, ion_energy, focus voltage) values.


.. code-block:: python
    
    >>> from rga import RGA100 as RGA
    >>> rga1 = RGA('tcpip','172.25.40.39','admin','admin')
    >>> rga1.reset()  # Reset RGA.
    >>> rga1.ionizer.get_parameters()  # It returns ionizer default values after reset.
    (70, 12, 90)
    >>> rga1.ionizer.set_parameters(60, 8, 100) # It returns error status. 0 means no error.
    0
    >>> rga1.ionizer.get_parameters()  # It returns the changed values.
    (60, 8, 100)
    >>>

Turn on/off filament
----------------------

To generate ions using electron impact method, the filament should be turned on and
maintain stable electron emission current. Typically, an SRS RGA operates with the default emission current of 1 mA.
Turn off filament by setting the emission current to 0, when the RGA is not in use to extend the filament life time.

    * Use :meth:`rga.rga100.rga.RGA100.set_ionizer_parameters` to set the emission current.
    * Use :meth:`rga.rga100.rga.RGA100.get_ionizer_parameters` to get the emission current sett1ing. 

.. code-block:: python
    
    >>> from rga import RGA100 as RGA
    >>> rga1 = RGA('tcpip','172.25.40.39','admin','admin')
    >>> rga1.reset()  # Reset RGA.
    >>> rga1.get_emission_current()  # Emission current is 0.0 after reset
    0.0
    >>> rga1.set_emission_current(1.0) # It returns 0 if no error occured during turning on the filament.
    0
    >>> rga1.get_emission_current() # It returns the filament emission current.
    0.9993

Setup scan parameters
-----------------------

Setting scan parameters controls how the `quadrupole mass filter <https://en.wikipedia.org/wiki/Quadrupole_mass_analyzer>`_
behaves during an analog  scan or histogram scan. During a scan the quadrupole mass filter steps up from the initial mass
to the final mass at the scan speed, with the specified step  per AMU.

    * Use :meth:`rga.rga100.rga.RGA100.scan.set_parameters` to set the scan parameters.
    * Use :meth:`rga.rga100.rga.RGA100.scan.get_parameters` to get the scan parameters.

.. code-block:: python

    >>> from rga import RGA100 as RGA
    >>> rga1 = RGA('tcpip','172.25.40.39','admin','admin')
    >>> rga1.reset()  # Resetting an SRS RGA also reset the scan parameters to default.
    >>> rga1.scan.get_parameters()  # returns (initial mass, final mass, scan speed, steps per AMU)
    (1, 200, 4, 10)
    >>> rga1.scan.set_parameters(10, 50, 1, 20) # Set the initial mass to 10, the final mass to 50,
    >>>                                         # scan speed to 1, and steps per AMU to 20.
    >>> rga1.scan.get_parameters()
    (10, 50, 1, 20)

Setup detector
-----------------

SRS RGA has two detectors: Faraday cup (FC) and Channel Electron multiplier (CEM).
When the CEM voltage is zero, it detects ion current without amplification.
When the CEM voltage is set to non-zero value, it detects amplified ion current using the CEM.

    * Use :meth:`rga.rga100.rga.RGA100.set_cem_voltage` to set the CEM voltage.
    * Use :meth:`rga.rga100.rga.RGA100.get_cem_voltage` to get the CEM voltage.

A CEM calibration is to finds how high CEM voltage is required to get the amplification gain you want,
and save the value for future use. You may run CEM calibration from an application,
not from the ``rga`` package.

    * Use :meth:`rga.rga100.rga.RGA100.get_cem_gain` to retrieve the saved CEM gain used in the last calibration.
    * Use :meth:`rga.rga100.rga.RGA100.get_calibrated_cem_voltage` to retrieve the saved CEM voltage
      for the CEM gain used in the last calibration.
    * Use :meth:`rga.rga100.rga.RGA100.turn_cem_on` to set the CEM voltage to the saved CEM voltage, or to 0.

.. code-block:: python

    >>> from rga import RGA100 as RGA
    >>> rga1 = RGA('tcpip','172.25.40.39','admin','admin')
    >>>
    >>> # Set CEM voltage to calibrated CEM voltage, or 0 to turn off.
    >>> calibrated_cem_voltage = rga1.get_calibrated_cem_voltage()
    >>> rga1.set_cem_voltage(calibrated_cem_voltage)  # CEM is on, It returns the error status.
    0
    >>>
    >>> # or simply set turn_cem_in on off state True/False
    >>> rga1.turn_cem_on(False) # CEM is off. It returns the error status.
    0
    >>> # Read back CEM voltage setting
    >>> rga1.get_cem_voltage()  # CEM voltage is 0, and Faraday cup detector is used.
    0

