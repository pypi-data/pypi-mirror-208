"""
Define real-time i/o blocks for use in block diagrams.  These are blocks that:

- have inputs or outputs
- have no state variables
- are a subclass of ``SourceBlock`` or ``SinkBlock``

"""
# The constructor of each class ``MyClass`` with a ``@block`` decorator becomes a method ``MYCLASS()`` of the BlockDiagram instance.

"""
could have if/else chain here to define these classes according to the platform
or define each hardware in its own file, protected by if platform


Need some kind of synchronous update, evaluate the network, then wait for 
sample time then update all analog blocks.  Perhaps a new kachunk method.
"""

# class _AnalogIn(Source):
#     pass

# class _AnalogOut(Sink):
#     pass

# class _PWMOut(Sink):
#     pass

# class _DigitalIn(Source):
#     pass

# class _DigitalOut(Sink):
#     pass

# """
# digital i/o, specify a number a list of bit ports
# """

# class _Screen(Sink):
#     pass


# The constructor of each class ``MyClass`` with a ``@block`` decorator becomes a method ``MYCLASS()`` of the BlockDiagram instance.

from bdsim.components import SinkBlock, SourceBlock

# from pymata4 import pymata4


class DOUT(SinkBlock):

    """
    :blockname:`DOUT`

    .. table::
       :align: left

    +--------+---------+---------+
    | inputs | outputs |  states |
    +--------+---------+---------+
    | 0      | 1       | 0       |
    +--------+---------+---------+
    |        | float,  |         |
    |        | A(N,)   |         |
    +--------+---------+---------+
    """

    nin = 1
    nout = 0

    def __init__(self, pin=0, **blockargs):
        """
        Constant value.

        :param value: the constant, defaults to 0
        :type value: any, optional
        :param blockargs: |BlockOptions|
        :type blockargs: dict
        :return: a CONSTANT block
        :rtype: Constant instance

        This block has only one output port, but the value can be any
        Python type, for example float, list or Numpy ndarray.
        """
        super().__init__(**blockargs)
        DIGITAL_PIN = 13  # arduino pin number
        self.pin = pin
        # self.board = pymata4.Pymata4()
        # self.board.set_pin_mode_digital_output(pin)

    def step(self, t, inports):
        value = self.inputs[0]
        # self.board.digital_write(self.pin, value)
        print(f"{value} --> pin {self.pin}")


# ------------------------------------------------------------------------ #
