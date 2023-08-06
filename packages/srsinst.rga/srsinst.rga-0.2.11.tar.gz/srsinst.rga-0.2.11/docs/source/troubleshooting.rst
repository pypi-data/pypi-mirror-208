
Troubleshooting
================

Communication troubleshooting
------------------------------------

If you are not lucky with typo, incorrect cabling, or computer firewall, you will see quite a long error message sayting timeout. You need to fix the problem to proceed. 

    .. code-block:: python

        >>> rga1 = rga.RGA100('tcpip', '172.25.140.39', 'admin', 'admin')
        Traceback (most recent call last):
          File "C:\PyPI\rga\rga\baseinsts\communications.py", line 492, in open
            self.socket.connect((ip_address, port))
        socket.timeout: timed out

        During handling of the above exception, another exception occurred:

        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "C:\PyPI\rga\rga\rga100\rga.py", line 22, in __init__
            super().__init__(interface_type, *args)
          File "C:\PyPI\rga\rga\baseinsts\instrument.py", line 65, in __init__
            Instrument.open(self, interface_type, *args)  # make sure not to run a subclass method
          File "C:\PyPI\rga\rga\baseinsts\instrument.py", line 78, in open
            self.comm.open(*args)
          File "C:\PyPI\rga\rga\baseinsts\communications.py", line 495, in open
            raise Interface.InstCommunicationError('Timeout connecting to ' + str(ip_address))
        rga.baseinsts.communications.InstCommunicationError: Timeout connecting to 172.25.140.39
        >>>