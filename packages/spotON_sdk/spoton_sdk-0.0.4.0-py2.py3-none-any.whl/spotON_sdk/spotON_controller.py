from typing import List
from dataclasses import dataclass


from spotON_sdk.settings.Feedback import Feedback
from spotON_sdk.settings.Config import Config
from spotON_sdk.settings.Switchtypes import Switchtypes



@dataclass
class Controller():
    name :str
    config  : Config
    feedback : List[Feedback]
    output_Switch : Switchtypes