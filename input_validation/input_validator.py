import pandas as pd 

from enum import Enum, IntEnum


from pydantic import BaseModel, ValidationError

class ModalityEnum(str, Enum):
    identification = 'identification'
    replay = 'replay'

class ModalityValidator(BaseModel):
    modality: ModalityEnum



class InputValidator():
    def __init__(self, modality):
        self.modality = modality


    def validate(self):
        try:
            ModalityValidator(modality=self.modality)
        except ValidationError as e:
            raise e


