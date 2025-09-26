from __future__ import annotations

from functools import lru_cache
from typing import Iterable, Literal, Tuple

import numpy as np
from pint import Quantity, UnitRegistry

UnitSystem = Literal["si", "us"]


@lru_cache(maxsize=1)
def get_unit_registry() -> UnitRegistry:
    ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
    ureg.define("percent = 0.01 dimensionless = %")
    ureg.define("gallon_us = gallon")
    ureg.define("gpm = gallon_us / minute")
    ureg.define("ftH2O = foot * water_density * gravity / (kilogram / meter**2)")
    return ureg


def format_units(unit: Quantity | str) -> str:
    if isinstance(unit, Quantity):
        unit = unit.units
    return f"{unit:~P}"


def ensure_quantity(values: Iterable[float] | np.ndarray, unit: str) -> Quantity:
    ureg = get_unit_registry()
    return np.asarray(list(values)) * ureg(unit)


def to_si(quantity: Quantity) -> Quantity:
    return quantity.to_base_units()


def convert(quantity: Quantity, unit: str) -> Quantity:
    ureg = get_unit_registry()
    return quantity.to(ureg(unit))


def parse_value(value: float, unit: str) -> Quantity:
    ureg = get_unit_registry()
    return value * ureg(unit)


def convert_array(values: Iterable[float], from_unit: str, to_unit: str) -> np.ndarray:
    quantity = ensure_quantity(values, from_unit)
    converted = convert(quantity, to_unit)
    return np.asarray(converted.magnitude, dtype=float)


def unit_system_defaults(system: UnitSystem) -> Tuple[str, str]:
    if system == "us":
        return "gallon_us/minute", "foot"
    return "meter**3/second", "meter"

