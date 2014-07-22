from spynnaker.pyNN.models.neural_properties.\
    synapse_dynamics.abstract_synapse_row_io import AbstractSynapseRowIo
from spynnaker.pyNN.models.neural_properties.synapse_row_info import \
    SynapseRowInfo
from spynnaker.pyNN import exceptions
import numpy
#ABS the noinspections are due to a problem mapping from non static to static
#  methods. Current thoughts from rowley and i are that itll clean up in the
# wash and that its just pycharm being stupid again


class FixedSynapseRowIO(AbstractSynapseRowIo):

    # noinspection PyMethodOverriding
    @staticmethod
    def read_packed_plastic_plastic_region(synapse_row, data, offset,
                                           length, weight_scale):
        raise exceptions.SynapticConfigurationException("fixed synapse rows do"
                                                        "not contain a plastic "
                                                        "region")

    # noinspection PyMethodOverriding
    @staticmethod
    def get_n_words(synapse_row, lo_atom=None, hi_atom=None):
        return synapse_row.get_n_connections(lo_atom, hi_atom)

    # noinspection PyMethodOverriding
    @staticmethod
    def get_packed_fixed_fixed_region(synapse_row, weight_scale,
                                      n_synapse_type_bits):
        abs_weights = numpy.abs(synapse_row.weights)
        scaled_weights = numpy.asarray(abs_weights * weight_scale,
                                       dtype='uint32')
        
        if ((len(synapse_row.target_indices) > 0) 
                and (numpy.amax(synapse_row.target_indices) > 0xFF)):
            raise Exception("One or more target indices are too large")
        
        max_delay = (1 << (8 - n_synapse_type_bits)) - 1
        if ((len(synapse_row.delays) > 0) 
                and (max(synapse_row.delays) > max_delay)):
            raise Exception("One or more delays are too large for the row")
        
        ids = synapse_row.target_indices & 0xFF
        shifted_weights = scaled_weights << 16
        shifted_delays = synapse_row.delays << (8 + n_synapse_type_bits)
        shifted_types = synapse_row.synapse_types << 8

        return numpy.asarray(shifted_weights | shifted_delays
                             | shifted_types | ids, dtype='uint32')

    # noinspection PyMethodOverriding
    @staticmethod
    def get_packed_fixed_plastic_region(synapse_row, weight_scale,
                                        n_synapse_type_bits):
        return []

    # noinspection PyMethodOverriding
    @staticmethod
    def get_packed_plastic_region(synapse_row, weight_scale,
                                  n_synapse_type_bits):
        return []

    # noinspection PyMethodOverriding
    @staticmethod
    def create_row_info_from_elements(p_p_entries, f_f_entries,
                                      f_p_entries, bits_reserved_for_type,
                                      weight_scale):
        """
        takes a collection of entries for both fixed fixed, plastic plasitic and
        fixed plastic and returns a synaptic row object for them

        p_p_entries and f_p_entries are ignored due to this model dealing with
        fixed synapses
        """
        if len(p_p_entries) > 0 or len(f_p_entries) > 0:
            raise exceptions.SynapticBlockGenerationException(
                "fixed synaptic row ios cannot be built from plastic entries"
            )
        target_indices = list()
        weights = list()
        delays_in_ticks = list()
        synapse_types = list()

        #read in each element
        for element in f_f_entries:
            # drops delay, type and id
            weights.append(float(element >> 16) / float(weight_scale))
            target_indices.append(element & 0xFF)  # masks by 8 bits
            # gets the size of the synapse type parameter
            synaptic_type_mask = (1 << bits_reserved_for_type) - 1
            synapse_types.append((element >> 8) & synaptic_type_mask)
            delay_mask = (1 << (8 - bits_reserved_for_type)) - 1
            delays_in_ticks.append((element >> 8 + bits_reserved_for_type) &
                                   delay_mask)

        return SynapseRowInfo(target_indices, weights, delays_in_ticks,
                              synapse_types)