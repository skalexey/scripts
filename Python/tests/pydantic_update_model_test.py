from test import *

def pydantic_update_model_test():
	log(title("Pydantic Update Model Test"))
	from pydantic import BaseModel, create_model, Field
	from typing import Type, Any, Dict, Tuple

	def update_model(base_model: Type[BaseModel], *modules: Type[BaseModel]) -> Type[BaseModel]:
		"""
		Creates a new Pydantic model dynamically by merging a base model with multiple modules.
		Handles nested models correctly in Pydantic v1 and applies default values.
		"""
		def resolve_field_type(field_type: Type, field_default: Any) -> Tuple[Type, Any]:
			"""If the field is a Pydantic model, find and apply the correct module overrides."""
			if isinstance(field_type, type) and issubclass(field_type, BaseModel):
				# Find modules that extend this specific nested model
				nested_modules = [m for m in modules if issubclass(m, field_type)]
				if nested_modules:
					return update_model(field_type, *nested_modules), field_default
			return field_type, field_default

		# Collect fields from the base model (Pydantic v1 uses __annotations__)
		fields: Dict[str, Tuple[Type, Any]] = {
			name: resolve_field_type(field_type, getattr(base_model, name, None))
			for name, field_type in base_model.__annotations__.items()
		}

		# Ensure fields from all modules are included (fixes missing fields issue)
		for module in modules:
			for name, field_type in module.__annotations__.items():
				default_value = getattr(module, name, getattr(base_model, name, None))
				fields[name] = resolve_field_type(field_type, default_value)

		# Create a new model dynamically
		return create_model(f"{base_model.__name__}Updated", **fields)



	# ---- Usage Example ----

	def test_pydantic_update_model_with_nested_fields():
		# ---- Define Models ----
		# Nested Model
		class AddressModel(BaseModel):
			city: str
			zip_code: str

		# Base Model
		class UserModel(BaseModel):
			id: int
			name: str
			age: int = 30
			address: AddressModel

		# ---- Define Modules (Updates) ----
		# Module 1 - Add `email` to `UserModel`
		class UserModule1(BaseModel):
			email: str = "default@example.com"

		# Module 2 - Add `state` to `AddressModel`
		class AddressModule1(BaseModel):
			state: str = "Unknown"  # New field in AddressModel

		# Module 3 - Add `phone` to `UserModel`
		class UserModule2(BaseModel):
			phone: str = "000-000-0000"

		# ---- Generate Updated Model (Including Nested Updates) ----
		UpdatedUserModel = update_model(UserModel, UserModule1, UserModule2)
		UpdatedAddressModel = update_model(AddressModel, AddressModule1)

		# ---- Assertions for Model Structure ----
		# Ensure new fields are added
		assert "email" in UpdatedUserModel.__annotations__, "email field not added correctly"
		assert "phone" in UpdatedUserModel.__annotations__, "phone field not added correctly"
		assert "state" in UpdatedAddressModel.__annotations__, "state field not added correctly"

		# ---- Instantiate Objects & Validate ----
		user1 = UpdatedUserModel(
			id=1,
			name="Alice",
			email="alice@example.com",
			phone="123-456-7890",
			address={"city": "NY", "zip_code": "12345", "state": "NY"}
		)

		user2 = UpdatedUserModel(
			id=2,
			name="Bob",
			address={"city": "LA", "zip_code": "90001"}  # Should use default state="Unknown"
		)

		# ---- Assertions for Object Values ----
		# User 1
		assert user1.email == "alice@example.com", "email value incorrect"
		assert user1.phone == "123-456-7890", "phone value incorrect"
		assert user1.address.city == "NY", "city value incorrect"
		assert user1.address.zip_code == "12345", "zip_code incorrect"
		assert user1.address.state == "NY", "state value incorrect"

		# User 2 (Defaults Applied)
		assert user2.email == "default@example.com", "default email not applied"
		assert user2.phone == "000-000-0000", "default phone not applied"
		assert user2.address.city == "LA", "city value incorrect"
		assert user2.address.zip_code == "90001", "zip_code incorrect"
		assert user2.address.state == "Unknown", "default state not applied"

		print("✅ All assertions passed successfully!")


	test_pydantic_update_model_with_nested_fields()

def test():
	pydantic_update_model_test()

run()
