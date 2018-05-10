from six import add_metaclass
from enum import Enum
from spinn_utilities.abstract_base import AbstractBase, abstractproperty


class MatrixGeneratorID(Enum):
    STATIC_MATRIX = 0
    STDP_MATRIX = 1


@add_metaclass(AbstractBase)
class AbstractGenerateOnMachine(object):

    def generate_on_machine(self):
        """ Determines if this instance should be generated on the machine.

        Default implementation returns True

        :rtype: bool
        """
        return True

    @abstractproperty
    def gen_on_machine_matrix_id(self):
        """ The ID of the on-machine matrix generator

        :rtype: int
        """

    @abstractproperty
    def gen_on_machine_matrix_params(self):
        """ Any parameters required by the matrix generator

        :rtype: numpy array of uint32
        """