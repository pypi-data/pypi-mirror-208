from operator import __ge__ 
from operator import __le__ 

from dataclasses import dataclass,field
from ..Config import *
from .Sensors import *

class Comperators():
    greater_equals = __ge__
    lower_equas = __le__

@dataclass
class Feedback():
    sensor : Sensor
    target_value : float
    comparator:Comperators
    def polling(self):
        return self.comparator(self.sensor.value, self.target_value)
    





