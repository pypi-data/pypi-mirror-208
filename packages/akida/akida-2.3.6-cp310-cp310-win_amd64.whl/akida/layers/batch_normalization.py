from akida.core import (Layer, LayerParams, LayerType)


class BatchNormalization(Layer):
    """Batch Normalization applied on the last axis.

    The normalization is applied as:

    outputs = a * x + b

    Args:
        output_bits (int, optional): output bitwidth. Defaults to 8.
        buffer_bits (int, optional): buffer bitwidth. Defaults to 32.
        activation (bool, optional): add a ReLU activation. Defaults to False.
        name (str, optional): name of the layer. Defaults to empty string.
    """

    def __init__(self,
                 output_bits=8,
                 buffer_bits=32,
                 activation=False,
                 name=""):
        try:
            params = LayerParams(
                LayerType.BatchNormalization, {
                    "output_bits": output_bits,
                    "buffer_bits": buffer_bits,
                    "activation": activation,
                })
            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except BaseException:
            self = None
            raise
