from data_specification.enums.data_type import DataType
from spinn_utilities.overrides import overrides
from spynnaker.pyNN.models.neuron.plasticity.stdp.weight_dependence\
    .abstract_weight_dependence import AbstractWeightDependence


class WeightDependenceRecurrent(AbstractWeightDependence):

    def __init__(self, 
        w_min_excit  =1.0, w_max_excit  =2.0, A_plus_excit  =3.0, A_minus_excit  =4.0,
        w_min_excit2 =5.0, w_max_excit2 =6.0, A_plus_excit2 =7.0, A_minus_excit2 =8.0,
        w_min_inhib  =9.0, w_max_inhib  =10.0, A_plus_inhib  =11.0, A_minus_inhib  =12.0,
        w_min_inhib2 =13.0, w_max_inhib2 =14.0, A_plus_inhib2 =15.0, A_minus_inhib2 =16.0):

        AbstractWeightDependence.__init__(self)
        self._w_min_excit    = w_min_excit
        self._w_max_excit    = w_max_excit
        self._A_plus_excit   = A_plus_excit
        self._A_minus_excit  = A_minus_excit
        self._w_min_excit2   = w_min_excit2
        self._w_max_excit2   = w_max_excit2
        self._A_plus_excit2  = A_plus_excit2
        self._A_minus_excit2 = A_minus_excit2
        self._w_min_inhib    = w_min_inhib
        self._w_max_inhib    = w_max_inhib
        self._A_plus_inhib   = A_plus_inhib
        self._A_minus_inhib  = A_minus_inhib
        self._w_min_inhib2   = w_min_inhib2
        self._w_max_inhib2   = w_max_inhib2
        self._A_plus_inhib2  = A_plus_inhib2
        self._A_minus_inhib2 = A_minus_inhib2

    @property
    def w_min(self):
        return self._w_min_excit

    @property
    def w_max(self):
        return self._w_max_excit

    @property
    def A_plus(self):
        return self._A_plus_excit

    @property
    def A_minus(self):
        return self._A_minus_excit

    def is_same_as(self, weight_dependence):
        if not isinstance(weight_dependence, WeightDependenceRecurrent):
            return False
        return (
            (self._w_min_excit   == weight_dependence._w_min_excit)  and
            (self._w_max_excit   == weight_dependence._w_max_excit)  and
            (self._A_plus_excit  == weight_dependence._A_plus_excit) and
            (self._A_minus_excit == weight_dependence._A_minus_excit))

    @property
    def vertex_executable_suffix(self):
        return "multiplicative"

    def get_parameters_sdram_usage_in_bytes(
            self, n_synapse_types, n_weight_terms):
        if n_weight_terms != 1:
            raise NotImplementedError(
                "Multiplicative weight dependence only supports single terms")

        numParams = 4
        paramSz   = 4
        return (numParams * paramSz) * n_synapse_types

    def write_parameters(
            self, spec, machine_time_step, weight_scales, n_weight_terms):
        if n_weight_terms != 1:
            raise NotImplementedError(
                "Multiplicative weight dependence only supports single terms")

        spec.write_value( data=int(round(self._w_min_excit * weight_scales[0]   )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._w_max_excit * weight_scales[0]   )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._A_plus_excit* weight_scales[0]   )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._A_minus_excit * weight_scales[0] )), data_type=DataType.INT32)

        spec.write_value( data=int(round(self._w_min_excit2 * weight_scales[1]  )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._w_max_excit2 * weight_scales[1]  )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._A_plus_excit2 * weight_scales[1] )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._A_minus_excit2 * weight_scales[1])), data_type=DataType.INT32)

        spec.write_value( data=int(round(self._w_min_inhib * weight_scales[2]   )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._w_max_inhib * weight_scales[2]   )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._A_plus_inhib * weight_scales[2]  )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._A_minus_inhib * weight_scales[2] )), data_type=DataType.INT32)

        spec.write_value( data=int(round(self._w_min_inhib2 * weight_scales[3]  )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._w_max_inhib2 * weight_scales[3]  )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._A_plus_inhib2 * weight_scales[3] )), data_type=DataType.INT32)
        spec.write_value( data=int(round(self._A_minus_inhib2* weight_scales[3] )), data_type=DataType.INT32)


    @property
    def weight_maximum(self):
        return self._w_max_excit

    @overrides(AbstractWeightDependence.get_parameter_names)
    def get_parameter_names(self):
        return ['w_min', 'w_max', 'A_plus', 'A_minus']
