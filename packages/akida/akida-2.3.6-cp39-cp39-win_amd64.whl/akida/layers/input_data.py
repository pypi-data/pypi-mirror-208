from akida.core import (Layer, LayerParams, LayerType)


class InputData(Layer):
    """This layer is used to specify the input dimensions of a low bitwidth Model.

    Models accepting 8-bit images must start with an InputConvolutional layer,
    but layers accepting integer inputs with a lower bitwidth (i.e. not images)
    and layers accepting signed inputs must start instead with an InputData
    layer.
    This layer does not modify its inputs: it just allows to define the Model
    input dimensions and bitwidth.

    Args:
        input_shape (tuple): the 3D input shape.
        input_bits (int, optional): input bitwidth. Defaults to 4.
        input_signed (bool, optional): whether the input is signed or not.
            Defaults to False.
        name (str, optional): name of the layer. Defaults to empty string.

    """

    def __init__(self, input_shape, input_bits=4, input_signed=False, name=""):
        try:
            params = LayerParams(
                LayerType.InputData, {
                    "input_width": input_shape[0],
                    "input_height": input_shape[1],
                    "input_channels": input_shape[2],
                    "input_signed": 1 if input_signed else 0,
                    "input_bits": input_bits
                })

            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except BaseException:
            self = None
            raise
