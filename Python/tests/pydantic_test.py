import pydantic

from test import *

from pydantic import BaseModel, Extra
from typing import Optional
from pydantic import Field

class StrictModel(BaseModel):
	"""
	A Pydantic model that does not allow fields not supported by this model to be added to it.
	"""

	class Config:  # pylint: disable=missing-class-docstring
		extra = Extra.forbid


def model_inheritance_test():
	log(title("Model Inheritance Test"))
	
	class A(StrictModel):
		a: Optional[int]

	class B(A):
		b: Optional[int]

	class C(StrictModel):
		c: Optional[A]

	data = { "c": { "a": 3 } }
	model = C(**data)

	# C.__annotations__["c"] = Optional[B]
	# data = { "c": { "a": 3, "b": 4 } }
	# with AssertException(pydantic.ValidationError):
	# 	model = C(**data)

	class D(C):
		c: Optional[B]

	data = { "c": { "a": 3, "b": 4 } }
	model = D(**data)
	log(title("End of Model Inheritance Test"))

def pydantic_test():
	log(title("Pydantic Test"))
	model_inheritance_test()
	log(title("End of Pydantic Test"))

def test():
	pydantic_test()

run()
