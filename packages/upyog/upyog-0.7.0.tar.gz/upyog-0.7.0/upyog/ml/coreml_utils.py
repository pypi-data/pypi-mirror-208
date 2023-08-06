from upyog.ml.imports import *
import coremltools as ct


__all__ = ["get_coreml_input"]


# TODO: Get from upyog
def get_coreml_input(
    H: int,
    W: int,
    norm_mean: Optional[Tuple[float, float, float]] = (0.485, 0.456, 0.406),
    norm_stdev: Optional[Tuple[float, float, float]] = (0.229, 0.224, 0.225),
    input_name: str = "Image",
    input_format: Literal["RGB", "BGR"] = "RGB",
) -> List[ct.ImageType]:
    """
    Get CoreML input image type to feed into a model. If using `norm_mean` and
    `norm_stdev`, it does preprocessing as described (ImageNet example) here:
    https://github.com/apple/coremltools/issues/1160

    If `norm_mean` or `norm_stdev` is None, inputs are are not normalised
    and are in the range of 0-255 (as is the case for YOLOX)

    Returns a list so you can call the function inside the converter alone
        `ct.convert(model, inputs = get_coreml_input(...))`
    """
    if norm_mean and norm_stdev:
        assert len(norm_mean) == 3 and len(norm_stdev) == 3
        scale_div = sum(norm_stdev) / len(norm_stdev)
        scale = 1.0 / (255.0 * scale_div)
        bias = list(map(lambda x: -x / scale_div, norm_mean))
    else:
        scale = 1.0
        bias = None

    input_type = ct.ImageType(
        input_name,
        shape=torch.rand(1, 3, H, W).shape,
        scale=scale,
        bias=bias,
        color_layout=input_format,
    )
    return [input_type]