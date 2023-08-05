import sys
from functools import lru_cache
from typing import Type, Dict, Any, ForwardRef, _eval_type
from importlib import import_module
from enum import Enum
from gstorm import BaseGraphQLType


def is_enum(x):
    return Enum in type(x).__mro__


def is_gql_subtype(x):
    return BaseGraphQLType in type(x).__mro__


def enum_cast(x):
    return x.value if is_enum(x) else x


def convert_to(models_path, classname):
    """Returns a casting function to determined type
    Parameters
    ----------
    models_path : str
      String denoting the path to the models directory: "path.to.models"
    classname : str
      Model name (Ej: "Author", "User", etc)
    Returns
    -------
    function
      function to cast to the specified type
    Raises
    ------
    Exception
      When the class was not found in the available models
    """
    models = import_module(models_path)

    def concrete_cast(value):
        if hasattr(models, classname):
            cls = getattr(models, classname)
        else:
            raise Exception(
                f'"{classname}" model not found inside models module ({models_path})')
        '''casts to specified type'''
        if value is None:
            return None
        if type(value) == dict:
            return cls(**value)
        elif type(value) == str or is_enum(value):
            return cls(value)
        elif is_gql_subtype(value):
            return value
        else:
            return value
    return concrete_cast


def list_convert_to(models_path: str, classname: str):
    """Returns a casting function to determined type

    Parameters
    ----------
    models_path : str
      module path where to look for GraphQL models (ej: "tests.models")
    classname : str
      concrete type to convert-to

    Returns
    -------
    function
        function to cast to the specified type
    """
    models = import_module(models_path)

    def concrete_cast(values):
        if hasattr(models, classname):
            cls = getattr(models, classname)
        else:
            raise Exception(
                f'"{classname}" model not found inside models module ({models_path})')
        '''casts list items to specified type'''
        casted_values = []
        for value in values:
            if type(value) == dict:
                casted_values.append(cls(**value))
            elif type(value) == cls:
                init_values = {
                    k: v for k, v in value.__dict__.items() if not k.startswith('_')}
                casted_values.append(cls(**init_values))
        return casted_values
    return concrete_cast


def gql_repr(value):
    if value is None:
        return 'None'
    return f'{type(value).__name__}(...)'


def gql_list_repr(values):
    if values is None:
        return 'None'
    if len(values) == 0:
        return '[]'
    else:
        return f'[{type(values[0]).__name__}({len(values)})]'


@lru_cache
def attrs_with_hints(model: Type) -> Dict[str, Any]:
    """Method to return the attributes of a given class
    with the corresponding hints.

    Args:
    ------
        - model (Type): Model to obtain its attributes with hints

    Return:
    ------
        - Dict with the attr as key and the hint as value
    """
    mapped_attrs: Dict[str, Any] = {}  # Dictionary for the attributes
    for base_class in model.__mro__:
        # Iterate over the annotations of the base class
        for key, hint in base_class.__dict__.get("__annotations__", {}).items():
            # Obtain the import from the file where it resides this base class
            global_variables = sys.modules[base_class.__module__].__dict__
            if hint in global_variables:
                mapped_attrs[key] = global_variables[hint]
            elif hint in global_variables["__builtins__"]:
                mapped_attrs[key] = global_variables["__builtins__"][hint]
            else:
                # For those that are not directly in the global variables, try to evaluate them
                # as a forward reference. For Python <=3.8, it would not fail the `try` block and
                # it would work as expected. In Python >=3.8, if it fail with a `NameError`, then
                # it's an GraphQLType model.
                try:
                    mapped_attrs[key] = _eval_type(
                        ForwardRef(hint), global_variables, locals())
                except NameError:
                    mapped_attrs[key] = ForwardRef(hint)
    return mapped_attrs
