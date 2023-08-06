from typing import Optional

from deci_common.abstractions.base_model import Schema
from deci_common.data_types.enum.hardware_enums import (
    HardwareEnvironment,
    HardwareGroup,
    HardwareImageDistribution,
    HardwareImageRepository,
    HardwareLabel,
    HardwareMachineModel,
    HardwareTaint,
    HardwareType,
    HardwareTypeLabel,
    HardwareVendor,
    InferenceHardware,
    MapHardwareTypeToEnvironment,
    MapHardwareTypeToFamily,
    MapHardwareTypeToGroup,
    MapHardwareTypeToImageDistribution,
    MapHardwareTypeToImageRepository,
    MapHardwareTypeToVendor,
)


# TODO move all hardwaretype usage to use thic class insted.
class HardwareReturnSchema(Schema):
    """
    A logic schema of hardware
    """

    name: HardwareType
    label: HardwareTypeLabel
    vendor: Optional[HardwareVendor] = None
    machine: Optional[HardwareMachineModel] = None
    group: Optional[HardwareGroup] = None
    future: bool = False
    deprecated: bool = False


class Hardware(Schema):
    """
    A logic schema of hardware
    """

    name: HardwareType
    type: InferenceHardware
    # equals None for backwards compatibility of benchmark jobs who does not have it.
    machine: Optional[HardwareMachineModel] = None
    cost_per_hour: int = 0
    environment: Optional[HardwareEnvironment]
    vendor: HardwareVendor
    label: HardwareLabel
    taint: HardwareTaint
    image_repository: Optional[HardwareImageRepository]
    image_distribution: Optional[HardwareImageDistribution]


def get_hardware_by_hardware_name(hw_name: HardwareType) -> Hardware:
    if type(hw_name) is str:
        hw_name = HardwareType(hw_name)
    inference_hardware = MapHardwareTypeToFamily[hw_name.name].value
    image_repository = getattr(MapHardwareTypeToImageRepository, hw_name.name, None)
    image_distribution = getattr(MapHardwareTypeToImageDistribution, hw_name.name, None)
    hardware_environment = getattr(MapHardwareTypeToEnvironment, hw_name.name, None)
    return Hardware(
        name=hw_name,
        type=inference_hardware,  # type: ignore[arg-type]
        environment=hardware_environment.value if hardware_environment is not None else None,
        taint=HardwareTaint[hw_name.name],
        machine=HardwareMachineModel[hw_name.name],
        vendor=HardwareVendor.INTEL if inference_hardware == InferenceHardware.CPU else HardwareVendor.NVIDIA,
        label=HardwareLabel[hw_name.name],
        image_repository=image_repository.value if image_repository is not None else None,
        image_distribution=image_distribution.value if image_distribution is not None else None,
    )


def get_hardware_return_schema(hw_name: HardwareType) -> HardwareReturnSchema:
    if type(hw_name) is str:
        hw_name = HardwareType(hw_name)
    return HardwareReturnSchema(
        name=hw_name,
        label=HardwareTypeLabel[hw_name.name],
        vendor=MapHardwareTypeToVendor[hw_name.name].value if hasattr(MapHardwareTypeToVendor, hw_name.name) else None,  # type: ignore[arg-type]
        machine=HardwareMachineModel[hw_name.name],
        group=MapHardwareTypeToGroup[hw_name.name].value,  # type: ignore[arg-type]
        future=hw_name.is_future,
        deprecated=hw_name.is_deprecated,
    )
