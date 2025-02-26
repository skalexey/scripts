# pylint: disable=unused-variable
# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring

from typing import Optional
import pytest
from utils.parse.function_parser import load_function


class NavigationStep:
    def __init__(self, variables, **data):
        self.function: Optional[str] = data.get("function")
        self.bound_function = load_function(self.function, variables)


class TestFunctionParser:
    def test_just_args(self, mocker):
        callback_mock = mocker.Mock()

        def navstep_func_just_args(x, y, z):
            callback_mock(x, y, z)

        variables = {"just_args": navstep_func_just_args}
        string = "(10, 20, 30)"
        nav_step = NavigationStep(variables, function="just_args" + string)
        nav_step.bound_function()
        callback_mock.assert_called_once_with(10, 20, 30)

    def test_just_kwargs(self, mocker):
        callback_mock = mocker.Mock()

        def navstep_func_just_kwargs(x=10, y=20, z=30):
            callback_mock(x, y, z)

        variables = {"just_kwargs": navstep_func_just_kwargs}
        string = "(x=10, y=20, z=30)"
        nav_step = NavigationStep(variables, function="just_kwargs" + string)
        nav_step.bound_function()
        callback_mock.assert_called_once_with(10, 20, 30)

    def test_mixed_args_kwargs(self, mocker):
        callback_mock = mocker.Mock()

        def navstep_func_mixed_args_kwargs(x, y, z=30):
            callback_mock(x, y, z)

        variables = {"mixed_args_kwargs": navstep_func_mixed_args_kwargs}
        string = "(10, 20, z=30)"
        nav_step = NavigationStep(variables, function="mixed_args_kwargs" + string)
        nav_step.bound_function()
        callback_mock.assert_called_once_with(10, 20, 30)

    def test_just_string_args(self, mocker):
        callback_mock = mocker.Mock()

        def navstep_func_just_string_args(x, y, z):
            callback_mock(x, y, z)

        variables = {"just_string_args": navstep_func_just_string_args}
        string = '("apple", "banana", "cherry")'
        nav_step = NavigationStep(variables, function="just_string_args" + string)
        nav_step.bound_function()
        callback_mock.assert_called_once_with("apple", "banana", "cherry")

    def test_just_single_quoted_string_args(self, mocker):
        callback_mock = mocker.Mock()

        def navstep_func_just_single_quoted_string_args(x, y, z):
            callback_mock(x, y, z)

        variables = {"just_single_quoted_string_args": navstep_func_just_single_quoted_string_args}
        string = "('apple', 'banana', 'cherry')"
        nav_step = NavigationStep(variables, function="just_single_quoted_string_args" + string)
        nav_step.bound_function()
        callback_mock.assert_called_once_with("apple", "banana", "cherry")

    def test_mixed_number_string_args(self, mocker):
        callback_mock = mocker.Mock()

        def navstep_func_mixed_number_string_args(x, y, z):
            callback_mock(x, y, z)

        variables = {"mixed_number_string_args": navstep_func_mixed_number_string_args}
        string = "(10, 'banana', z='value')"
        nav_step = NavigationStep(variables, function="mixed_number_string_args" + string)
        nav_step.bound_function()
        callback_mock.assert_called_once_with(10, "banana", "value")

    def test_no_args(self, mocker):
        callback_mock = mocker.Mock()

        def navstep_func_no_args():
            callback_mock()

        variables = {"no_args": navstep_func_no_args}
        string = "()"
        nav_step = NavigationStep(variables, function="no_args" + string)
        nav_step.bound_function()
        callback_mock.assert_called_once()

    def test_positional_order_mismatch(self, mocker):
        callback_mock = mocker.Mock()

        def navstep_func_positional_order_mismatch(x, y, z=3):
            callback_mock(x, y, z)

        variables = {"positional_order_mismatch": navstep_func_positional_order_mismatch}
        string = "(1, z=2, 3)"
        with pytest.raises(ValueError) as raises_exception:
            nav_step = NavigationStep(variables, function="positional_order_mismatch" + string)
            nav_step.bound_function()
        assert str(raises_exception.value) == "Positional arguments cannot appear after keyword arguments"
        callback_mock.assert_not_called()

    def test_stack_argument(self, mocker):
        callback_mock = mocker.Mock()
        ext_obj = "External object"

        def navstep_func_stack_argument(a, ext=ext_obj):
            callback_mock(a, ext)

        variables = {"stack_argument": navstep_func_stack_argument}
        string = "(3, ext_obj)"
        nav_step = NavigationStep(variables, function="stack_argument" + string)
        nav_step.bound_function()
        callback_mock.assert_called_once_with(3, ext_obj)

    # Test nested quotes in string arguments
    # console_command("a_cmd 0 1 \"name = 'smth'\"")
    def test_nested_quotes(self, mocker):
        callback_mock = mocker.Mock()

        def navstep_func_nested_quotes(str_arg):
            callback_mock(str_arg)

        variables = {"nested_quotes": navstep_func_nested_quotes}
        string = '("a_cmd 0 1 \\"name = \'smth\'\\"")'
        nav_step = NavigationStep(variables, function="nested_quotes" + string)
        nav_step.bound_function()
        callback_mock.assert_called_once_with("a_cmd 0 1 \"name = 'smth'\"")

    values = [
        ("(10, 20, 30)", (10, 20, 30), {}),
        ("(x=10, y=20, z=30)", (), {"x": 10, "y": 20, "z": 30}),
        ("(10, 20, z=30)", (10, 20), {"z": 30}),
        ('("apple", "banana", "cherry")', ("apple", "banana", "cherry"), {}),
        ("('apple', 'banana', 'cherry')", ("apple", "banana", "cherry"), {}),
        ("(10, 'banana', z='value')", (10, "banana"), {"z": "value"}),
        ("()", (), {}),
    ]

    @pytest.mark.parametrize("args_str, expected_args, expected_kwargs", values, ids=[i[0] for i in values])
    def test_func_any_args(self, mocker, args_str, expected_args, expected_kwargs):
        callback_mock = mocker.Mock()

        def navstep_func_any_args(*args, **kwargs):
            callback_mock(args, kwargs)

        variables = {"any_args": navstep_func_any_args}
        nav_step = NavigationStep(variables, function="any_args" + args_str)
        nav_step.bound_function()
        callback_mock.assert_called_once_with(expected_args, expected_kwargs)
