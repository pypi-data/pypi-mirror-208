from dataclasses import dataclass, field

from scipy import constants

import math


@dataclass
class Constants:
    # name: str
    # lon: float = field(default=0.0, metadata={'unit': 'degrees'})
    # lat: float = field(default=0.0, metadata={'unit': 'degrees'})

    hbar: float = constants.hbar
    mu_B: float = constants.physical_constants['Bohr magneton'][0]
    k_B: float = constants.Boltzmann
