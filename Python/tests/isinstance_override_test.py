import builtins
from test import *
from typing import Any


class ProxyMeta(type):
	def __instancecheck__(cls, instance):
		# Properly override isinstance behavior
		print(f"__instancecheck__ called: {cls}, instance: {instance}")
		if isinstance(instance, Proxy):
			return isinstance(instance._wrapped_obj, cls)
		return super().__instancecheck__(cls, instance)


class Proxy(metaclass=ProxyMeta):
	def __init__(self, wrapped_obj):
		self._wrapped_obj = wrapped_obj


class ProxyDerived(Proxy):
	pass


class ExampleClass:
	pass

# Doesn't work:
class my_type(type):
	def __instancecheck__(self, instance):
		if isinstance(instance, Proxy):
			return isinstance(instance._wrapped_obj, self)
		return super().__instancecheck__(instance)
type = my_type
__builtins__["type"] = my_type
# ^^^^^^^^^^^^^^^ Doesn't work ^^^^^^^^^^^^^^^^^^^^^^^^^^^
def isinstance_override_test():
	print("Start of `isinstance` Override Test")

	# Test objects
	wrapped_instance = ExampleClass()
	proxy_instance = Proxy(wrapped_instance)
	proxy_derived_instance = ProxyDerived(wrapped_instance)

	# Assertions
	assert isinstance(proxy_instance, Proxy)  # Should pass
	assert isinstance(proxy_derived_instance, ExampleClass)  # Should pass
	assert not isinstance(wrapped_instance, Proxy)  # Should pass

	print("End of `isinstance` Override Test")



def test():
	log(title("Isinstance Override Test"))
	isinstance_override_test()
	log(title("End of Isinstance Override Test"))

run()
