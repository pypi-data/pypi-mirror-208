# test.py

import pandas as pd
import numpy as np

from represent import BaseModel

class Model(BaseModel):

    def __init__(self) -> None:

        self.self = self
        self.type = type(self)

        self.values = [1, 2, 3]

        self.objects = {
            'self': self.self,
            'type': self.type,
            self.self: self.self,
            self.type: self.type,
            (1, 2, 3): self.values
        }
        self.objects['data'] = self.objects

        self.data = pd.DataFrame({1: [1, 2, 3]})
        self.array = np.array([[1, 2, 3], [4, 5, 6]])
    # end __init__
# Model

model = Model()

print(model)