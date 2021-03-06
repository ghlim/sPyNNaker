from spinn_utilities.overrides import overrides

from .abstract_ethernet_controller import AbstractEthernetController

from pacman.model.constraints.key_allocator_constraints import \
    FixedKeyAndMaskConstraint
from pacman.model.routing_info import BaseKeyAndMask

from spinn_front_end_common.abstract_models import \
    AbstractProvidesOutgoingPartitionConstraints
from spinn_front_end_common.utilities.exceptions import ConfigurationException
from spinn_front_end_common.abstract_models \
    import AbstractVertexWithEdgeToDependentVertices

from spynnaker.pyNN.models.neuron import AbstractPopulationVertex

import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class ExternalDeviceLifControlVertex(
        AbstractPopulationVertex,
        AbstractEthernetController,
        AbstractProvidesOutgoingPartitionConstraints,
        AbstractVertexWithEdgeToDependentVertices):
    """ Abstract control module for the pushbot, based on the LIF neuron,\
        but without spikes, and using the voltage as the output to the various\
        devices
    """

    # all commands will use this mask
    _DEFAULT_COMMAND_MASK = 0xFFFFFFFF

    def __init__(
            self, devices, create_edges, max_atoms_per_core, neuron_impl,
            pynn_model, translator=None, spikes_per_second=None, label=None,
            ring_buffer_sigma=None, incoming_spike_buffer_size=None,
            constraints=None):
        """
        :param n_neurons: The number of neurons in the population
        :param devices:\
            The AbstractMulticastControllableDevice instances to be controlled\
            by the population
        :param create_edges:\
            True if edges to the devices should be added by this dev (set\
            to False if using the dev over Ethernet using a translator)
        :param translator:\
            Translator to be used when used for Ethernet communication.  Must\
            be provided if the dev is to be controlled over Ethernet.
        """
        # pylint: disable=too-many-arguments, too-many-locals

        if not devices:
            raise ConfigurationException("No devices specified")

        # Create a partition to key map
        self._partition_id_to_key = OrderedDict(
            (str(dev.device_control_partition_id), dev.device_control_key)
            for dev in devices)

        # Create a partition to atom map
        self._partition_id_to_atom = {
            partition: i
            for (i, partition) in enumerate(self._partition_id_to_key.keys())
        }

        self._devices = devices
        self._message_translator = translator

        # Add the edges to the devices if required
        self._dependent_vertices = list()
        if create_edges:
            self._dependent_vertices = devices

        super(ExternalDeviceLifControlVertex, self).__init__(
            len(devices), label, constraints, max_atoms_per_core,
            spikes_per_second, ring_buffer_sigma, incoming_spike_buffer_size,
            neuron_impl, pynn_model)

    def routing_key_partition_atom_mapping(self, routing_info, partition):
        # pylint: disable=arguments-differ
        key = self._partition_id_to_key[partition.identifier]
        atom = self._partition_id_to_atom[partition.identifier]
        return [(atom, key)]

    @overrides(AbstractProvidesOutgoingPartitionConstraints.
               get_outgoing_partition_constraints)
    def get_outgoing_partition_constraints(self, partition):
        return [FixedKeyAndMaskConstraint([BaseKeyAndMask(
            self._partition_id_to_key[partition.identifier],
            self._DEFAULT_COMMAND_MASK)])]

    @overrides(AbstractVertexWithEdgeToDependentVertices.dependent_vertices)
    def dependent_vertices(self):
        return self._dependent_vertices

    @overrides(AbstractVertexWithEdgeToDependentVertices
               .edge_partition_identifiers_for_dependent_vertex)
    def edge_partition_identifiers_for_dependent_vertex(self, vertex):
        return [vertex.device_control_partition_id]

    @overrides(AbstractEthernetController.get_external_devices)
    def get_external_devices(self):
        return self._devices

    @overrides(AbstractEthernetController.get_message_translator)
    def get_message_translator(self):
        if self._message_translator is None:
            raise ConfigurationException(
                "This population was not given a translator, and so cannot be"
                "used for Ethernet communication.  Please provide a "
                "translator for the population.")
        return self._message_translator

    @overrides(AbstractEthernetController.get_outgoing_partition_ids)
    def get_outgoing_partition_ids(self):
        return self._partition_id_to_key.keys()
