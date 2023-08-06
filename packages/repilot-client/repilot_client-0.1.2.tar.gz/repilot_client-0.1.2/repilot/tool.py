import inspect
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, List

from pydantic import BaseModel, Field, create_model
from repilot.utils.schema_utils import minify_docstring


@dataclass
class Tool:
    name: str
    pydoc: str | None
    signature: str
    basemodel: BaseModel
    return_type: str
    func: Callable
    is_async: bool = False

    @property
    def minified_doc(self):
        if self.pydoc is None:
            return ""
        return minify_docstring(self.pydoc.split(":param")[0])

    def __repr__(self):
        return f"{self.name}:{self.minified_doc} {self.json_schema}"

    @property
    def json_schema(self):
        return self.basemodel.schema()["properties"]

    @property
    def details(self):
        return {
            "name": self.name,
            "doc": self.minified_doc,
            "signature": self.signature,
            "return_type": self.return_type,
            "json_schema": self.json_schema,
            "is_async": self.is_async,
        }


class ToolKit:
    def __init__(self, init_func: Callable | None = None):
        self.tools: List[Tool] = []
        self.tools_dict: Dict[str, Tool] = {}
        if init_func:
            init_func(self)

    def register(self, func: Callable) -> Callable:
        # Dynamically generate Pydantic request model based on function arguments
        args_annotations = getattr(func, "__annotations__", {})
        inputs_annotations = {
            k: v for k, v in args_annotations.items() if k != "return"
        }

        # Get function signature for default values
        sig = inspect.signature(func)
        params = sig.parameters

        # Define a dictionary to store the field definitions for the Pydantic model
        field_definitions: Dict[str, Any] = {}
        for arg_name, arg_type in inputs_annotations.items():
            # Use the argument name as the field name
            field_name = arg_name
            # Use the argument type and any additional validation constraints from
            # annotations to define the field type
            default_value = (
                params[arg_name].default
                if params[arg_name].default != inspect.Parameter.empty
                else ...
            )
            field_definitions[field_name] = (arg_type, Field(default_value))

        # Dynamically create a Pydantic model from the field definitions
        Request = create_model("InputModel", **field_definitions)
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get parameter names from function signature
            params = inspect.signature(func).parameters.keys()
            # Match parameter values with names and convert them to a dictionary
            kwargs.update(zip(params, args))
            # Create request object from validated kwargs
            request = Request(**kwargs)
            # Call original function with validated and converted kwargs
            return func(**request.dict())

        # Create tool object and append it to the tools list
        tool = Tool(
            name=func.__name__,
            pydoc=func.__doc__,
            basemodel=Request,
            signature=str(inspect.signature(func)),
            return_type=func.__annotations__["return"].__name__
            if "return" in func.__annotations__
            else None,
            func=wrapper,
            is_async=is_async,
        )
        self.tools.append(tool)
        self.tools_dict[func.__name__] = tool

        return wrapper

    def tool_names(self):
        return [tool.name for tool in self.tools]

    def __getitem__(self, item):
        return self.tools_dict[item]

    def __iter__(self):
        return iter(self.tools)

    def __len__(self):
        return len(self.tools)

    def __repr__(self):
        return f"ToolKit({self.tools})"
