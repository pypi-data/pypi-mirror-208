from enum import Enum

# TODO: rename HardwareType to HardwareName and inferenceHardware to HardwareType
from typing import Optional

from deci_common.data_types.enum.models_enums import BatchSize, BatchSizeEdge
from deci_common.helpers import get_enum_values

UNKNOWN = "UNKNOWN"


class HardwareType(str, Enum):
    """
    The type of the hardware to run on (CPU/GPU Names)
    """

    K80 = "K80"
    V100 = "V100"
    T4 = "T4"
    A10G = "A10G"
    G4DN_XLARGE = "g4dn.xlarge"
    G5_XLARGE = "g5.xlarge"
    A100_80G = "A100 80GB GCP"
    A100_40G = "A100 40GB GCP"
    EPYC = "EPYC"
    EPYC_7002 = "EPYC 7002"
    EPYC_7003 = "EPYC 7003"
    XAVIER = "Jetson Xavier"
    NANO = "Jetson Nano"
    XAVIER_AGX = "Jetson Xavier AGX"
    ORIN = "Jetson Orin"
    ORIN_NX = "Jetson Orin NX"
    ORIN_NANO = "Jetson Orin Nano"
    ORIN_NANO_4G = "Jetson Orin Nano 4GB"
    CASCADE_LAKE = "Cascade Lake"
    SKYLAKE = "Skylake"
    Broadwell = "Broadwell"
    Icelake = "Icelake"
    NUC_TIGER_LAKE = "Intel NUC Tiger Lake"
    SKYLAKE_SP = "Skylake-SP"
    CASCADE_LAKE_GCP = "Cascade Lake GCP"
    IMX8 = "NXP i.MX 8M mini"
    C5_2XLARGE = "c5.2xlarge"

    HAILO8 = "Hailo-8"
    AMBARELLA = "Ambarella"
    APPLE_IPHONE_A11 = "Apple iPhone A11"
    APPLE_IPHONE_A12 = "Apple iPhone A12"
    APPLE_IPHONE_A14 = "Apple iPhone A14"
    APPLE_IPHONE_A15 = "Apple iPhone A15"
    SNAPDRAGON_845 = "Snapdragon 845"
    SNAPDRAGON_855 = "Snapdragon 855"
    SNAPDRAGON_885 = "Snapdragon 888"
    SNAPDRAGON_8_GEN_1 = "Snapdragon 8 Gen 1"
    EXYNOS_9810 = "Exynos 9810"
    EXYNOS_9820 = "Exynos 9820"
    EXYNOS_990 = "Exynos 990"
    EXYNOS_2200 = "Exynos 2200"

    @property
    def is_future(self) -> bool:
        return self in [
            HardwareType.HAILO8,
            HardwareType.AMBARELLA,
            HardwareType.APPLE_IPHONE_A11,
            HardwareType.APPLE_IPHONE_A12,
            HardwareType.APPLE_IPHONE_A14,
            HardwareType.APPLE_IPHONE_A15,
            HardwareType.SNAPDRAGON_845,
            HardwareType.SNAPDRAGON_855,
            HardwareType.SNAPDRAGON_885,
            HardwareType.SNAPDRAGON_8_GEN_1,
            HardwareType.EXYNOS_9810,
            HardwareType.EXYNOS_9820,
            HardwareType.EXYNOS_990,
            HardwareType.EXYNOS_2200,
        ]

    @property
    def is_deprecated(self) -> bool:
        return self in [HardwareType.K80, HardwareType.EPYC]


class HardwareGroup(str, Enum):
    CPU = "CPU"
    GPU = "GPU"
    COMMERCIAL_EDGE = "Commercial Edge"
    CONSUMER_EDGE = "Consumer Edge"


class HardwareMachineModel(str, Enum):
    K80 = "p2.xlarge"
    V100 = "p3.2xlarge"
    T4 = "g4dn.2xlarge"
    A10G = "g5.2xlarge"
    G4DN_XLARGE = "g4dn.xlarge"
    G5_XLARGE = "g5.xlarge"
    EPYC = "c5a.2xlarge"
    CASCADE_LAKE = "c5.4xlarge"
    SKYLAKE = "c5n.4xlarge"
    Broadwell = "m4.4xlarge"
    Icelake = "m6i.4xlarge"
    EPYC_7002 = "c5a.4xlarge"
    EPYC_7003 = "m6a.4xlarge"
    SKYLAKE_SP = "m5.2xlarge"
    A100_40G = "a2-highgpu-1g"
    A100_80G = "a2-ultragpu-1g"
    CASCADE_LAKE_GCP = "n2-standard-4"
    C5_2XLARGE = "c5.2xlarge"

    NANO = HardwareType.NANO.value
    XAVIER = HardwareType.XAVIER.value
    XAVIER_AGX = HardwareType.XAVIER_AGX.value
    ORIN = HardwareType.ORIN.value
    ORIN_NX = HardwareType.ORIN_NX.value
    ORIN_NANO = HardwareType.ORIN_NANO.value
    ORIN_NANO_4G = HardwareType.ORIN_NANO_4G.value
    NUC_TIGER_LAKE = HardwareType.NUC_TIGER_LAKE.value
    IMX8 = HardwareType.IMX8.value
    HAILO8 = HardwareType.HAILO8.value
    AMBARELLA = HardwareType.AMBARELLA.value
    APPLE_IPHONE_A11 = HardwareType.APPLE_IPHONE_A11.value
    APPLE_IPHONE_A12 = HardwareType.APPLE_IPHONE_A12.value
    APPLE_IPHONE_A14 = HardwareType.APPLE_IPHONE_A14.value
    APPLE_IPHONE_A15 = HardwareType.APPLE_IPHONE_A15.value
    SNAPDRAGON_845 = HardwareType.SNAPDRAGON_845.value
    SNAPDRAGON_855 = HardwareType.SNAPDRAGON_855.value
    SNAPDRAGON_885 = HardwareType.SNAPDRAGON_885.value
    SNAPDRAGON_8_GEN_1 = HardwareType.SNAPDRAGON_8_GEN_1.value
    EXYNOS_9810 = HardwareType.EXYNOS_9810.value
    EXYNOS_9820 = HardwareType.EXYNOS_9820.value
    EXYNOS_990 = HardwareType.EXYNOS_990.value
    EXYNOS_2200 = HardwareType.EXYNOS_2200.value


class InferenceHardware(str, Enum):
    """
    Hardware that can be used for deep learning inference.
    """

    CPU = "cpu"
    GPU = "gpu"


class MapHardwareTypeToFamily(str, Enum):
    # GPUs
    V100 = InferenceHardware.GPU.value
    K80 = InferenceHardware.GPU.value
    T4 = InferenceHardware.GPU.value
    A10G = InferenceHardware.GPU.value
    G4DN_XLARGE = InferenceHardware.GPU.value
    G5_XLARGE = InferenceHardware.GPU.value
    A100_80G = InferenceHardware.GPU.value
    A100_40G = InferenceHardware.GPU.value
    NANO = InferenceHardware.GPU.value
    XAVIER = InferenceHardware.GPU.value
    XAVIER_AGX = InferenceHardware.GPU.value
    ORIN = InferenceHardware.GPU.value
    ORIN_NX = InferenceHardware.GPU.value
    ORIN_NANO = InferenceHardware.GPU.value
    ORIN_NANO_4G = InferenceHardware.GPU.value

    # CPUs
    EPYC = InferenceHardware.CPU.value
    EPYC_7002 = InferenceHardware.CPU.value
    EPYC_7003 = InferenceHardware.CPU.value
    CASCADE_LAKE = InferenceHardware.CPU.value
    SKYLAKE = InferenceHardware.CPU.value
    Broadwell = InferenceHardware.CPU.value
    Icelake = InferenceHardware.CPU.value
    NUC_TIGER_LAKE = InferenceHardware.CPU.value
    SKYLAKE_SP = InferenceHardware.CPU.value
    CASCADE_LAKE_GCP = InferenceHardware.CPU.value
    IMX8 = InferenceHardware.CPU.value
    C5_2XLARGE = InferenceHardware.CPU.value


class InferyVersion(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    JETSON = "jetson"
    JETSON_PY36 = "jetson_py36"
    JETSON_PY38 = "jetson_py38"


class MapHardwareTypeToInferyVersion(str, Enum):
    # GPUs
    V100 = InferyVersion.GPU.value
    K80 = InferyVersion.GPU.value
    T4 = InferyVersion.GPU.value
    A10G = InferyVersion.GPU.value
    G4DN_XLARGE = InferyVersion.GPU.value
    G5_XLARGE = InferyVersion.GPU.value
    A100_80G = InferyVersion.GPU.value
    A100_40G = InferyVersion.GPU.value

    # Jetsons
    NANO = InferyVersion.JETSON_PY36.value
    XAVIER = InferyVersion.JETSON_PY38.value
    XAVIER_AGX = InferyVersion.JETSON_PY36.value
    ORIN = InferyVersion.JETSON_PY38.value
    ORIN_NX = InferyVersion.JETSON_PY38.value
    ORIN_NANO = InferyVersion.JETSON_PY38.value
    ORIN_NANO_4G = InferyVersion.JETSON_PY38.value

    # CPUs
    EPYC = InferyVersion.CPU.value
    EPYC_7002 = InferyVersion.CPU.value
    EPYC_7003 = InferyVersion.CPU.value
    CASCADE_LAKE = InferyVersion.CPU.value
    SKYLAKE = InferyVersion.CPU.value
    Broadwell = InferyVersion.CPU.value
    Icelake = InferyVersion.CPU.value
    NUC_TIGER_LAKE = InferyVersion.CPU.value
    SKYLAKE_SP = InferyVersion.CPU.value
    CASCADE_LAKE_GCP = InferyVersion.CPU.value
    IMX8 = InferyVersion.CPU.value
    C5_2XLARGE = InferyVersion.CPU.value


class HardwareEnvironment(str, Enum):
    GCP = "gcp"
    AWS = "aws"
    Azure = "azure"
    PREMISE = "on premise"


class HardwareVendor(str, Enum):
    INTEL = "intel"
    NVIDIA = "nvidia"
    AMD = "amd"
    NXP = "nxp"


class HardwareTaint(str, Enum):
    # GPUs
    V100 = "nvidia.com/v100gpu"
    K80 = "nvidia.com/k80gpu"
    T4 = "nvidia.com/t4gpu"
    A10G = "nvidia.com/a10gpu"
    G4DN_XLARGE = "nvidia.com/g4dn-xlarge"
    G5_XLARGE = "nvidia.com/g5-xlarge"
    A100_80G = "nvidia.com/a100gpu80g"
    A100_40G = "nvidia.com/a100gpu40g"
    NANO = "nvidia.com/jetson-nano"
    XAVIER = "nvidia.com/jetson-xavier"
    XAVIER_AGX = "nvidia.com/jetson-xavier-agx"
    ORIN = "nvidia.com/jetson-orin"
    ORIN_NX = "nvidia.com/jetson-orin-as-nx16"
    ORIN_NANO = "nvidia.com/jetson-orin-as-nano"
    ORIN_NANO_4G = "nvidia.com/jetson-orin-as-nano4g"
    # CPUs
    EPYC = "amd.com/epyc"
    EPYC_7002 = "amd.com/7002"
    EPYC_7003 = "amd.com/7003"
    CASCADE_LAKE = "intel.com/cascade-lake"
    SKYLAKE = "intel.com/skylake"
    Broadwell = "intel.com/broadwell"
    Icelake = "intel.com/icelake"
    NUC_TIGER_LAKE = "intel.com/nuc-tiger-lake"
    SKYLAKE_SP = "intel.com/skylake-sp"
    CASCADE_LAKE_GCP = "intel.com/xeon"
    IMX8 = UNKNOWN
    C5_2XLARGE = "intel.com/c5-2xlarge"


class HardwareLabel(str, Enum):
    # GPUs
    V100 = "nvidia-tesla-v100"
    K80 = "nvidia-tesla-k80"
    T4 = "nvidia-tesla-t4"
    A10G = "nvidia-ampere-a10"
    G4DN_XLARGE = "nvidia-g4dn-xlarge"
    G5_XLARGE = "nvidia-g5-xlarge"
    A100_80G = "nvidia-a100-80g"
    A100_40G = "nvidia-a100-40g"
    NANO = "nvidia-jetson-nano"
    XAVIER = "nvidia-jetson-xavier"
    XAVIER_AGX = "nvidia-jetson-xavier-agx"
    ORIN = "nvidia-jetson-orin"
    ORIN_NX = "nvidia-jetson-orin-as-nx16"
    ORIN_NANO = "nvidia-jetson-orin-as-nano"
    ORIN_NANO_4G = "nvidia-jetson-orin-as-nano4g"

    # CPUs
    EPYC = "amd-epyc"
    EPYC_7002 = "amd-epyc-7002"
    EPYC_7003 = "amd-epyc-7003"
    CASCADE_LAKE = "intel-cascade-lake"
    SKYLAKE = "intel-skylake"
    Broadwell = "intel-broadwell"
    Icelake = "intel-icelake"
    NUC_TIGER_LAKE = "intel-nuc-tiger-lake"
    SKYLAKE_SP = "intel-skylake-sp"
    CASCADE_LAKE_GCP = "intel-xeon"
    IMX8 = UNKNOWN
    C5_2XLARGE = "intel-c5-2xlarge"


class MapHardwareTypeToVendor(str, Enum):
    V100 = HardwareVendor.NVIDIA.value
    K80 = HardwareVendor.NVIDIA.value
    T4 = HardwareVendor.NVIDIA.value
    A10G = HardwareVendor.NVIDIA.value
    G4DN_XLARGE = HardwareVendor.NVIDIA.value
    G5_XLARGE = HardwareVendor.NVIDIA.value
    A100_80G = HardwareVendor.NVIDIA.value
    A100_40G = HardwareVendor.NVIDIA.value
    EPYC = HardwareVendor.AMD.value
    EPYC_7002 = HardwareVendor.AMD.value
    EPYC_7003 = HardwareVendor.AMD.value
    NANO = HardwareVendor.NVIDIA.value
    XAVIER = HardwareVendor.NVIDIA.value
    XAVIER_AGX = HardwareVendor.NVIDIA.value
    ORIN = HardwareVendor.NVIDIA.value
    ORIN_NX = HardwareVendor.NVIDIA.value
    ORIN_NANO = HardwareVendor.NVIDIA.value
    ORIN_NANO_4G = HardwareVendor.NVIDIA.value
    CASCADE_LAKE = HardwareVendor.INTEL.value
    SKYLAKE = HardwareVendor.INTEL.value
    Broadwell = HardwareVendor.INTEL.value
    Icelake = HardwareVendor.INTEL.value
    NUC_TIGER_LAKE = HardwareVendor.INTEL.value
    SKYLAKE_SP = HardwareVendor.INTEL.value
    CASCADE_LAKE_GCP = HardwareVendor.INTEL.value
    C5_2XLARGE = HardwareVendor.INTEL.value
    IMX8 = HardwareVendor.NXP.value


class MapHardwareTypeToEnvironment(str, Enum):
    # AWS
    V100 = HardwareEnvironment.AWS.value
    K80 = HardwareEnvironment.AWS.value
    T4 = HardwareEnvironment.AWS.value
    A10G = HardwareEnvironment.AWS.value
    G4DN_XLARGE = HardwareEnvironment.AWS.value
    G5_XLARGE = HardwareEnvironment.AWS.value
    EPYC = HardwareEnvironment.AWS.value
    EPYC_7002 = HardwareEnvironment.AWS.value
    EPYC_7003 = HardwareEnvironment.AWS.value
    CASCADE_LAKE = HardwareEnvironment.AWS.value
    SKYLAKE = HardwareEnvironment.AWS.value
    Broadwell = HardwareEnvironment.AWS.value
    Icelake = HardwareEnvironment.AWS.value
    SKYLAKE_SP = HardwareEnvironment.AWS.value
    C5_2XLARGE = HardwareEnvironment.AWS.value

    # GCP
    A100_40G = HardwareEnvironment.GCP.value
    A100_80G = HardwareEnvironment.GCP.value
    CASCADE_LAKE_GCP = HardwareEnvironment.GCP.value

    # PREMISE
    NANO = HardwareEnvironment.PREMISE.value
    XAVIER = HardwareEnvironment.PREMISE.value
    XAVIER_AGX = HardwareEnvironment.PREMISE.value
    ORIN = HardwareEnvironment.PREMISE.value
    ORIN_NX = HardwareEnvironment.PREMISE.value
    ORIN_NANO = HardwareEnvironment.PREMISE.value
    ORIN_NANO_4G = HardwareEnvironment.PREMISE.value
    NUC_TIGER_LAKE = HardwareEnvironment.PREMISE.value
    IMX8 = HardwareEnvironment.PREMISE.value


class MapHardwareTypeToDefaultBatchSizeList(list, Enum):  # type: ignore[type-arg]
    V100 = get_enum_values(BatchSize)
    K80 = get_enum_values(BatchSize)
    T4 = get_enum_values(BatchSize)
    A10G = get_enum_values(BatchSize)
    G4DN_XLARGE = get_enum_values(BatchSize)
    G5_XLARGE = get_enum_values(BatchSize)
    A100_80G = get_enum_values(BatchSize)
    A100_40G = get_enum_values(BatchSize)
    EPYC = get_enum_values(BatchSize)
    EPYC_7002 = get_enum_values(BatchSize)
    EPYC_7003 = get_enum_values(BatchSize)
    NANO = get_enum_values(BatchSizeEdge)
    XAVIER = get_enum_values(BatchSizeEdge)
    XAVIER_AGX = get_enum_values(BatchSizeEdge)
    ORIN = get_enum_values(BatchSizeEdge)
    ORIN_NX = get_enum_values(BatchSizeEdge)
    ORIN_NANO = get_enum_values(BatchSizeEdge)
    ORIN_NANO_4G = get_enum_values(BatchSizeEdge)
    CASCADE_LAKE = get_enum_values(BatchSize)
    SKYLAKE = get_enum_values(BatchSize)
    Broadwell = get_enum_values(BatchSize)
    Icelake = get_enum_values(BatchSize)
    NUC_TIGER_LAKE = get_enum_values(BatchSize)
    SKYLAKE_SP = get_enum_values(BatchSize)
    CASCADE_LAKE_GCP = get_enum_values(BatchSize)
    IMX8 = get_enum_values(BatchSize)
    C5_2XLARGE = get_enum_values(BatchSize)


class HardwareImageRepository(str, Enum):
    INTEL = "intel"
    JETSON = "jetson"


class MapHardwareTypeToImageRepository(str, Enum):
    NANO = HardwareImageRepository.JETSON.value
    XAVIER = HardwareImageRepository.JETSON.value
    XAVIER_AGX = HardwareImageRepository.JETSON.value
    ORIN = HardwareImageRepository.JETSON.value
    ORIN_NX = HardwareImageRepository.JETSON.value
    ORIN_NANO = HardwareImageRepository.JETSON.value
    ORIN_NANO_4G = HardwareImageRepository.JETSON.value
    NUC_TIGER_LAKE = HardwareImageRepository.INTEL.value


class HardwareImageDistribution(str, Enum):
    J46 = "j46"
    J50 = "j50"
    J502 = "j502"

    @property
    def python_version(self) -> str:
        dist_to_version = {
            HardwareImageDistribution.J46: "3.6",
            HardwareImageDistribution.J50: "3.8",
            HardwareImageDistribution.J502: "3.8",
        }
        return dist_to_version[self]


class MapHardwareTypeToImageDistribution(str, Enum):
    NANO = HardwareImageDistribution.J46.value
    XAVIER = HardwareImageDistribution.J502.value
    XAVIER_AGX = HardwareImageDistribution.J46.value
    ORIN = HardwareImageDistribution.J502.value
    ORIN_NX = HardwareImageDistribution.J502.value
    ORIN_NANO = HardwareImageDistribution.J502.value
    ORIN_NANO_4G = HardwareImageDistribution.J502.value


class MapHardwareTypeToGroup(str, Enum):
    K80 = HardwareGroup.GPU.value
    V100 = HardwareGroup.GPU.value
    T4 = HardwareGroup.GPU.value
    A10G = HardwareGroup.GPU.value
    G4DN_XLARGE = HardwareGroup.GPU.value
    G5_XLARGE = HardwareGroup.GPU.value
    A100_80G = HardwareGroup.GPU.value
    A100_40G = HardwareGroup.GPU.value

    XAVIER = HardwareGroup.COMMERCIAL_EDGE.value
    NANO = HardwareGroup.COMMERCIAL_EDGE.value
    XAVIER_AGX = HardwareGroup.COMMERCIAL_EDGE.value
    ORIN = HardwareGroup.COMMERCIAL_EDGE.value
    ORIN_NX = HardwareGroup.COMMERCIAL_EDGE.value
    ORIN_NANO = HardwareGroup.COMMERCIAL_EDGE.value
    ORIN_NANO_4G = HardwareGroup.COMMERCIAL_EDGE.value
    NUC_TIGER_LAKE = HardwareGroup.COMMERCIAL_EDGE.value
    AMBARELLA = HardwareGroup.COMMERCIAL_EDGE.value
    HAILO8 = HardwareGroup.COMMERCIAL_EDGE.value
    IMX8 = HardwareGroup.COMMERCIAL_EDGE.value

    EPYC = HardwareGroup.CPU.value
    EPYC_7002 = HardwareGroup.CPU.value
    EPYC_7003 = HardwareGroup.CPU.value
    CASCADE_LAKE = HardwareGroup.CPU.value
    SKYLAKE = HardwareGroup.CPU.value
    Broadwell = HardwareGroup.CPU.value
    Icelake = HardwareGroup.CPU.value
    SKYLAKE_SP = HardwareGroup.CPU.value
    CASCADE_LAKE_GCP = HardwareGroup.CPU.value
    C5_2XLARGE = HardwareGroup.CPU.value

    APPLE_IPHONE_A11 = HardwareGroup.CONSUMER_EDGE.value
    APPLE_IPHONE_A12 = HardwareGroup.CONSUMER_EDGE.value
    APPLE_IPHONE_A14 = HardwareGroup.CONSUMER_EDGE.value
    APPLE_IPHONE_A15 = HardwareGroup.CONSUMER_EDGE.value
    SNAPDRAGON_845 = HardwareGroup.CONSUMER_EDGE.value
    SNAPDRAGON_855 = HardwareGroup.CONSUMER_EDGE.value
    SNAPDRAGON_885 = HardwareGroup.CONSUMER_EDGE.value
    SNAPDRAGON_8_GEN_1 = HardwareGroup.CONSUMER_EDGE.value
    EXYNOS_9810 = HardwareGroup.CONSUMER_EDGE.value
    EXYNOS_9820 = HardwareGroup.CONSUMER_EDGE.value
    EXYNOS_990 = HardwareGroup.CONSUMER_EDGE.value
    EXYNOS_2200 = HardwareGroup.CONSUMER_EDGE.value


def type_with_model(model: HardwareMachineModel, override_label: Optional[str] = None) -> str:
    return f"{override_label or HardwareType[model.name].value} ({model})"


class HardwareTypeLabel(str, Enum):
    XAVIER = "Jetson Xavier NX 16GB"
    NANO = "Jetson Nano 4GB"
    XAVIER_AGX = "Jetson AGX Xavier 32GB"
    ORIN = "Jetson AGX Orin Development Kit"
    ORIN_NX = "Jetson Orin NX 16GB"
    ORIN_NANO = "Jetson Orin Nano 8GB"
    ORIN_NANO_4G = "Jetson Orin Nano 4GB"
    EPYC = type_with_model(HardwareMachineModel.EPYC)
    EPYC_7002 = type_with_model(HardwareMachineModel.EPYC_7002, f"AMD Rome {HardwareType.EPYC_7002.value}")
    EPYC_7003 = type_with_model(HardwareMachineModel.EPYC_7003, f"AMD Milan {HardwareType.EPYC_7003.value}")
    CASCADE_LAKE = type_with_model(HardwareMachineModel.CASCADE_LAKE)
    SKYLAKE = type_with_model(HardwareMachineModel.SKYLAKE, "Sky Lake")
    Broadwell = type_with_model(HardwareMachineModel.Broadwell)
    Icelake = type_with_model(HardwareMachineModel.Icelake, "Ice Lake")
    K80 = type_with_model(HardwareMachineModel.K80)
    V100 = type_with_model(HardwareMachineModel.V100)
    SKYLAKE_SP = type_with_model(HardwareMachineModel.SKYLAKE_SP)
    T4 = type_with_model(HardwareMachineModel.T4)
    A10G = type_with_model(HardwareMachineModel.A10G)
    A100_40G = type_with_model(HardwareMachineModel.A100_40G, "A100 40GB")
    A100_80G = type_with_model(HardwareMachineModel.A100_80G, "A100 80GB")
    CASCADE_LAKE_GCP = type_with_model(HardwareMachineModel.CASCADE_LAKE_GCP, "Cascade Lake")

    NUC_TIGER_LAKE = HardwareType.NUC_TIGER_LAKE.value
    IMX8 = HardwareType.IMX8.value
    C5_2XLARGE = HardwareType.C5_2XLARGE.value
    G4DN_XLARGE = HardwareType.G4DN_XLARGE.value
    G5_XLARGE = HardwareType.G5_XLARGE.value
    HAILO8 = HardwareType.HAILO8.value
    AMBARELLA = HardwareType.AMBARELLA.value
    APPLE_IPHONE_A11 = HardwareType.APPLE_IPHONE_A11.value
    APPLE_IPHONE_A12 = HardwareType.APPLE_IPHONE_A12.value
    APPLE_IPHONE_A14 = HardwareType.APPLE_IPHONE_A14.value
    APPLE_IPHONE_A15 = HardwareType.APPLE_IPHONE_A15.value
    SNAPDRAGON_845 = HardwareType.SNAPDRAGON_845.value
    SNAPDRAGON_855 = HardwareType.SNAPDRAGON_855.value
    SNAPDRAGON_885 = HardwareType.SNAPDRAGON_885.value
    SNAPDRAGON_8_GEN_1 = HardwareType.SNAPDRAGON_8_GEN_1.value
    EXYNOS_9810 = HardwareType.EXYNOS_9810.value
    EXYNOS_9820 = HardwareType.EXYNOS_9820.value
    EXYNOS_990 = HardwareType.EXYNOS_990.value
    EXYNOS_2200 = HardwareType.EXYNOS_2200.value
