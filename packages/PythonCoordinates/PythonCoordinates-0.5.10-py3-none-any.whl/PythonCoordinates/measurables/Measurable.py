from __future__ import annotations
import math, datetime
from enum import Enum
from typing import Union
import numpy as np


class Measurable:
    def __init__(self):
        self.value = 0.0
        self.unit_symbols = []

    def underlying_value(self):
        return self.value

    def is_nan(self):
        return np.isnan(self.value)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if type(other) == type(self):
            return self.value == other.value

    def __truediv__(self, other) -> Union[float, None]:
        if type(other) == type(self):
            return self.value / other.value
        else:
            return None


class InvalidUnitOfMeasureException(Exception):
    def __init__(self, message='Invalid unit of measurement!'):
        self.message = message

    message = ''




