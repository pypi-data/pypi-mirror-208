from __future__ import annotations
from typing import Dict, List, Tuple, Optional, NamedTuple

import pyvisa

from .abc import BaseInstrument
from .constants import InstrumentType
from . import models


rm = pyvisa.ResourceManager()


def get_visa_resource_manager() -> pyvisa.highlevel.ResourceManager:
    """
    Get the VISA resource manager instance that is used globally by PyInst.

    Returns:
        The VISA resource manager.
    """
    return rm


def list_visa_resources() -> Tuple[str, ...]:
    """
    List the resource names of all the connected VISA instruments.

    Returns:
        A tuple of resource names of all the connected VISA instruments.
    """
    return rm.list_resources()


def list_visa_resources_info() -> Dict[str, pyvisa.highlevel.ResourceInfo]:
    """
    Returns a dictionary mapping resource names to resource extended information of all connected VISA instruments.

    Returns:
        Mapping of resource name to ResourceInfo.
    """
    return rm.list_resources_info()


def get_visa_resource_info(resource_name: str, extended: bool = True) -> pyvisa.highlevel.ResourceInfo:
    """
    Get the (extended) information of a particular VISA resource.

    Args:
        resource_name: The resource name or alias of the VISA instrument.
        extended: Also get extended information (ie. resource_class, resource_name, alias)

    Returns:
        The ResourceInfo.
    """
    return rm.resource_info(resource_name, extended)


class InstrumentModelInfo(NamedTuple):
    """Information of the instrument model."""

    model: str
    "The model string of the instrument."

    brand: str
    "The brand of the instrument."

    class_name: str
    "The name of the instrument model class."

    ins_type: InstrumentType
    "The ins_type property of the instrument model class."

    params: List[dict]
    "A list of dict to define the parameters required to init the instrument model class."

    details: Dict[str, str]
    "A dict of details to describe the instrument."

    def to_dict(self):
        """Return the instrument model information as a dict."""
        return {k: getattr(self, k) for k in self._fields}


def list_instrument_model_info(ins_type: Optional[InstrumentType] = None) -> Tuple[InstrumentModelInfo, ...]:
    """
    List information all the instrument models. If the parameter `ins_type` is defined, only the instrument models of the same type will be listed.

    Args:
        ins_type: Only list the instrument models with the same type.

    Returns:
        The information of instrument models.
    """

    model_list = []
    for i in models.__dict__:
        model_cls = models.__dict__[i]
        if i.startswith('Model') and issubclass(model_cls, BaseInstrument):
            if ins_type is not None and ins_type not in model_cls.ins_type:
                continue
            else:
                model_list.append(InstrumentModelInfo(
                    model=model_cls.model,
                    brand=model_cls.brand,
                    class_name=i,
                    ins_type=model_cls.ins_type,
                    params=model_cls.params,
                    details=model_cls.details,
                ))

    return tuple(model_list)


def deprecated_monkey_patch():
    """Add deprecated methods with monkey patch to make it compatible with 
    the old legacy versions.
    """
    from .deprecated import deprecated_monkey_patch
    deprecated_monkey_patch()
