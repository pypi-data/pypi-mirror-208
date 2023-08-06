# represent

A module for object and model representations as strings, with vast configurations,
colors, hidden and protected values, assignment operations, memory addresses and more.

first of all
------------

#### specifics:

- writen and owned by: Shahaf Frank-Shapir
- all the rights are saved for: Shahaf Frank-Shapir
- program version: 0.0.0
- programming languages: python 3.9.12 (100%)

before we start
---------------

#### description:

> - This module creates an easy-to-use, versatile dynamic system for representing python objects as strings.
> - The string representation can be achieved for any python object, through functional or object-oriented usage.
> - It is possible to configure many specific ways to display data, hide attributes, represent nested objects,
	> circular references, memory address, attribute names and values, indentation, and mor.

#### dependencies:

- opening:
  As for this is a really complex program, which uses a lot of modules, there are required dependencies needed
  in order to run the program. keep in mined the program was writen in python 3.9, so any python version lower
  than 3.9 might not work properly. Moreover, built-in python modules are being used, so keep that in mind.

- install app dependencies by writing the "-r" option to install the requirements
  writen in a file, and write the following line in the project directory:
````
pip install -r requirements.txt
````

run a test
-----------

#### run from windows command line (inside the project directory)
- run with python by writing to the command line in the project directory:
````
python test.py
````
- An example of code using the BaseModel class:
````python
from represent import BaseModel

import numpy as np
import pandas as pd

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
````
- An example of code using functions directly:
````python
from represent import to_string

import numpy as np
import pandas as pd

class Model:

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

print(to_string(model))
````
- Output:
```python
<__main__.Model object at 0x000002700983FE10>(
	self=<circular referenced object: <__main__.Model object at 0x000002700983FE10>>,
	type=<class  __main__.Model>,
	values=[
		1,
		2,
		3
	],
	objects={
		'self': <circular referenced object: <__main__.Model object at 0x000002700983FE10>>,
		'type': <class  __main__.Model>,
		<circular referenced object: <__main__.Model object at 0x000002700983FE10>>: <circular referenced object: <__main__.Model object at 0x000002700983FE10>>,
		<class  __main__.Model>: <class  __main__.Model>,
		(
			1,
			2,
			3
		)
		: [
			1,
			2,
			3
		],
		'data': {
			'self': <__main__.Model object at 0x000002700983FE10>,
			'type': <class '__main__.Model'>,
			<__main__.Model object at 0x000002700983FE10>: <__main__.Model object at 0x000002700983FE10>,
			<class '__main__.Model'>: <class '__main__.Model'>,
			(
				1,
				2, 
				3
			)
			: [
				1,
				2, 
				3
			],
			'data': {
				...
			}
		}
	},
	data=<pandas.core.frame.DataFrame object at 0x000002701AFC6110>(
		|   1|,
		|0  1|,
		|1  2|,
		|2  3|
	),
	array=<numpy.ndarray object at 0x000002701B84C330>(
		[
			[
				1,
				2,
				3,
			],
			[
				4,
				5,
				6,
			],
		]
	)
)
```