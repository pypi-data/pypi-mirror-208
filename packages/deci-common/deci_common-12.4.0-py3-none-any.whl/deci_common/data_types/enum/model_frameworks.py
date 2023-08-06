from enum import Enum
from typing import List, Optional

from deci_common.abstractions.base_model import Schema
from deci_common.data_types.enum.hardware_enums import InferenceHardware


class FileExtensions(Schema):
    main: str
    additional: List[str] = []
    raw: Optional[str] = None


class FrameworkFileExtension(Enum):
    TENSORFLOW1 = FileExtensions(main=".pb")
    TENSORFLOW2 = FileExtensions(main=".zip")
    PYTORCH = FileExtensions(main=".pth", additional=[".pt"])
    ONNX = FileExtensions(main=".onnx")
    TENSORRT = FileExtensions(main=".pkl", raw=".engine")
    OPENVINO = FileExtensions(main=".pkl", raw=".zip")
    TORCHSCRIPT = FileExtensions(main=".pth", additional=[".pt"])
    TVM = None
    KERAS = FileExtensions(main=".h5")
    TFLITE = FileExtensions(main=".tflite")
    COREML = FileExtensions(main=".mlmodel")
    TFJS = FileExtensions(main=".zip")


class FrameworkType(str, Enum):
    """
    A general deep learning framework, without a version.
    """

    TENSORFLOW1 = "tf1"
    TENSORFLOW2 = "tf2"
    PYTORCH = "pytorch"
    ONNX = "onnx"
    TORCHSCRIPT = "torchscript"
    TENSORRT = "trt"
    TVM = "tvm"
    OPENVINO = "openvino"
    KERAS = "keras"
    TFLITE = "tflite"
    COREML = "coreml"
    TFJS = "tfjs"

    @staticmethod
    def from_string(framework: str) -> Enum:
        framework = framework.lower()
        return FrameworkType(framework)


def get_hardware_families_by_framework_type(framework: FrameworkType) -> List[InferenceHardware]:
    if framework == FrameworkType.OPENVINO:
        return [InferenceHardware.CPU]
    elif framework == FrameworkType.TENSORRT:
        return [InferenceHardware.GPU]
    else:
        return [InferenceHardware.GPU, InferenceHardware.CPU]
