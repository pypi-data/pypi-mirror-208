from dataclasses import dataclass


@dataclass
class Parameter:
    value: float
    dimension: str
    system: str = 'SI'

