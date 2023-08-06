from dataclasses import dataclass,field
from .Units import Unit

@dataclass
class Sensor():
    value:float
    unit :Unit