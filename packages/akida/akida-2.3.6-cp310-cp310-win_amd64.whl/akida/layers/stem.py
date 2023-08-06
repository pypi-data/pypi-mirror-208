from akida.core import (Layer, LayerParams, LayerType)


class Stem(Layer):
    """Stem layer corresponding to the Stem block of Transformer models.

    It's composed of the following layers:

        - The Embedding layer
        - The Reshape layer
        - The ClassToken (+ DistToken for distilled model) layer(s)
        - The AddPosEmbedding layer

    This layer covers all the above layers operations.

    Note that final output values will be saturated on the range that can
    be represented with output_bits.

    Note: For now only the convolution operation of the Embedding layer
    is covered and the final output quantization.

    Args:
        input_shape (tuple): the spatially square 3D input shape.
        filters (int, optional): Positive integer, dimensionality of the output space.
            Defaults to 192.
        kernel_size (int, optional): kernel size. Defaults to 16.
        output_bits (int, optional): output bitwidth. Defaults to 8.
        buffer_bits (int, optional): buffer bitwidth. Defaults to 32.
        collapse_spatial_dims (bool, optional): boolean to trigger the output spatial
            dimensions collapse. Defaults to True.
        num_non_patch_tokens (int, optional): number of non patch tokens to concatenate
            with the input along it last axis. Defaults to 0.
        add_pos_embs_available (bool, optional): boolean to trigger the positional
            embedding matrix addition. Defaults to False.
        name (str, optional): name of the layer. Defaults to empty string.

    """

    def __init__(self,
                 input_shape,
                 filters=192,
                 kernel_size=16,
                 output_bits=8,
                 buffer_bits=32,
                 collapse_spatial_dims=True,
                 num_non_patch_tokens=0,
                 add_pos_embs_available=False,
                 name=""):
        try:
            if (input_shape[0] != input_shape[1]):
                raise ValueError(
                    "input should have square spatial dimensions."
                    f"Receives x_size={input_shape[0]} and y_size={input_shape[1]}"
                )

            params = LayerParams(
                LayerType.Stem, {
                    "input_spatial_size": input_shape[0],
                    "input_channels": input_shape[2],
                    "filters": filters,
                    "kernel_size": kernel_size,
                    "output_bits": output_bits,
                    "buffer_bits": buffer_bits,
                    "collapse_spatial_dims": collapse_spatial_dims,
                    "num_non_patch_tokens": num_non_patch_tokens,
                    "add_pos_embs_available": add_pos_embs_available
                })
            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except BaseException:
            self = None
            raise
