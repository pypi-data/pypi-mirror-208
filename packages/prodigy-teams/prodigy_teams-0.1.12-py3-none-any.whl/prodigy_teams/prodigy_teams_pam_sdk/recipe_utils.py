import inspect
import re
from enum import Enum

from pydantic import validator
from radicli import (
    DEFAULT_PLACEHOLDER,
    Arg,
    ArgparseArg,
    format_type,
    get_arg,
    get_list_converter,
)
from radicli.util import BASE_TYPES, join_strings

from . import models, ty
from .errors import RecipeProcessingError

SIMPLE_TYPES = {str: "str", int: "int", bool: "bool", float: "float", ty.UUID: "uuid"}
SIMPLE_TYPES_BY_NAME = {v: k for k, v in SIMPLE_TYPES.items()}
OBJECT_FIELD_KEYS = ("asset", "dataset", "secret")
UNPARSED = object()

# We can pass in Dict values because we might have Asset, Dataset
# etc fields in there.
PlanType = ty.Dict[str, ty.Union[ty.Dict, str, int, float, bool, ty.List[str]]]
ObjectsMapType = ty.Dict[str, ty.Dict[str, ty.Dict[str, ty.Any]]]
TypeCallbackType = ty.Callable[[str], ty.Optional[ty.Callable[..., ty.Any]]]
_InT = ty.TypeVar("_InT", bound=ty.Union[str, int, float])
_CustomT = ty.TypeVar("_CustomT")


def slugify_name(v: str) -> str:
    """Turn a user input readable string into a URL friendly slug without invalid characters"""
    input_name = re.sub("_", "-", v)
    input_name = re.sub(r"[^A-Za-z0-9\-\. ]", "", input_name)
    input_name = re.sub(r"\s+", "-", input_name)
    input_name = input_name.lower()
    return input_name


class Validation(models.ValidationSchema):
    # fmt: off
    op: ty.Union[models.ValidationOp, ty.Literal["ge", "gt", "le", "lt", "eq", "ne", "re"]]
    level: ty.Union[models.ValidationLevel, ty.Literal["error", "warning", "info", "success"]]
    # fmt: on


# Frustratingly, the SDK conversion process messes up defaults, which
# hurts quite a bit for these. So we redefine and set defaults.


class Props(ty.BaseModel):
    """Properties common to all types"""

    # Set defaults for type checker
    name: ty.Optional[str] = None
    title: ty.Optional[str] = None
    description: ty.Optional[str] = None
    placeholder: ty.Optional[str] = None
    value: ty.Optional[ty.Any] = None
    required: ty.Optional[bool] = None
    positional: ty.Optional[bool] = None
    exists: ty.Optional[bool] = None
    validations: ty.Optional[ty.List[models.ValidationSchema]] = None
    pattern: ty.Optional[str] = None  # HTML default regex validation
    widget: ty.Optional[str] = None
    choice: ty.Optional[ty.Dict[str, "Props"]] = None
    min: ty.Optional[float] = None
    max: ty.Optional[float] = None
    step: ty.Optional[float] = None
    optional_title: ty.Optional[str] = None


class OptionalProps(Props):
    """Properties for optional fields that provide an additional label for the toggle"""

    optional_title: ty.Optional[str] = None


class TextProps(Props):
    """Properties for text fields"""

    pattern: ty.Optional[str] = None  # HTML default regex validation
    widget: ty.Optional[ty.Literal["text", "textarea", "password"]] = None


class IntProps(Props):
    """Properties for int fields"""

    step: int = 1
    min: ty.Optional[int] = None
    max: ty.Optional[int] = None
    widget: ty.Optional[ty.Literal["number", "range"]] = None


class FloatProps(Props):
    """Properties for float fields"""

    step: float = 0.01
    min: ty.Optional[float] = None
    max: ty.Optional[float] = None
    widget: ty.Optional[ty.Literal["number", "range"]] = None


class BoolProps(Props):
    """Properties for bool fields"""

    widget: ty.Optional[ty.Literal["checkbox", "toggle"]] = None


class ChoiceProps(Props):
    """Properties for choice fields like Enum and Union"""

    # Additional properties for each choice
    choice: ty.Optional[ty.Dict[str, "AnyProps"]] = None
    widget: ty.Optional[ty.Literal["select", "radio"]] = None


class ListProps(Props):
    """Properties for List fields"""

    min: ty.Optional[int] = None  # Minimum number of items in the list
    max: ty.Optional[int] = None  # Maximum number of items in the list


AnyProps = ty.Union[
    IntProps, FloatProps, BoolProps, TextProps, ChoiceProps, ListProps, Props
]
ChoiceProps.update_forward_refs()


class Field(models.FieldSchema):
    # Set defaults for type checker compatibility
    props: Props
    fields: ty.List["Field"] = []
    choice: ty.List["Field"] = []

    # Subclassing the field here so we can slugify names
    @validator("name")
    def slugify_name(cls, v: str) -> str:
        return slugify_name(v)


class RecipeSchema(models.RecipeSchema):
    fields: ty.List[Field]
    title: ty.Optional[str] = None
    description: ty.Optional[str] = None
    view_id: ty.Optional[str] = None
    cli_names: ty.Dict[str, str] = {}


def get_field_optional(schema: models.RecipeSchema) -> ty.Dict[str, bool]:
    """Walk the schema, and map field names according to whether they're globally optional.
    A field is globally optional if it descends from a choice or a non-required
    field.
    """
    output = {}
    queue = [(not field.props.required, field) for field in schema.fields]
    for is_optional, field in queue:
        output[field.name] = is_optional
        # Fields of a custom type are optional if they descend from an optional, or
        # if they're not required
        sub_fields = field.fields or []
        queue.extend([(is_optional or not f.props.required, f) for f in sub_fields])
        # Everything descending from a choice (e.g. an object nested within a union) needs to
        # be marked optional
        queue.extend([(True, f) for f in (field.choice or [])])
    return output


def get_field_names(field: Field) -> ty.Set[str]:
    """Walk the field schema and get all of its parent and child names."""
    output = set()
    queue = [(f.name, f) for f in field.fields] + [(f.name, f) for f in field.choice]
    for name, field in queue:
        output.add(name)
        queue.extend(
            [(f.name, f) for f in field.fields] + [(f.name, f) for f in field.choice]
        )
    return output


def get_field_cli_type(
    field: Field, parent: ty.Optional[Field] = None
) -> ty.Tuple[ty.Type, ty.Optional[ty.Callable[[str], ty.Any]]]:
    if field.type.name in SIMPLE_TYPES_BY_NAME:
        return SIMPLE_TYPES_BY_NAME[field.type.name], None
    elif field.type.object_type in OBJECT_FIELD_KEYS:
        return str, None
    elif field.type.name == "list":
        type_args = ty.cast(ty.List[models.TypeSchema], field.type.args)
        arg_name = type_args[0].name if len(type_args) else "str"
        base_type = SIMPLE_TYPES_BY_NAME.get(arg_name, str)
        return ty.List[base_type], get_list_converter(base_type)
    elif field.type.name == "enum":
        enum_args = {f.name: f.props.value for f in field.choice}
        enum = Enum("str", enum_args)  # name for CLI help display purpose only
        # We currently expect all enum members to have the same type
        enum_type = type(field.choice[0].props.value) if field.choice else str
        base_type = enum_type if enum_type and enum_type in SIMPLE_TYPES else str
        return enum, lambda v: base_type(getattr(enum, v).value)
    elif field.type.name == "literal" and field.type.args:
        # Only handling string literals (also supported in schema only)
        enum = Enum("str", {k: k for k in field.type.args})
        return enum, lambda v: getattr(enum, v).value
    elif parent is not None and parent.type.name in ["union", "optional"]:
        # If we're an empty type within a union, make it a bool
        return bool, None
    else:
        return str, None


def get_field_cli_args(
    field: Field,
    cli_names: ty.Dict[str, str],
    name: ty.Optional[str] = None,
    parent: ty.Optional[Field] = None,
    force_optional: bool = False,
) -> ty.List[ArgparseArg]:
    name = name or field.props.name or field.name
    # If a field is optional, force everything underneath it to be optional
    force_optional = force_optional or not field.props.required
    if field.type.object_type in OBJECT_FIELD_KEYS:
        # Handle these as special cases: we only ask for their name
        return [
            _create_field_arg(
                cli_names.get(name, name), str, None, field.props, force_optional
            )
        ]
    elif len(field.fields) > 0:
        args = []
        # If the custom class is Optional we add the option of creating it with defaults
        if parent is not None and parent.type.name == "optional":
            arg_type, arg_converter = get_field_cli_type(field, parent=parent)
            if name in cli_names:
                name = cli_names[name]
            args.append(
                _create_field_arg(
                    name, arg_type, arg_converter, field.props, force_optional
                )
            )
        for subfield in field.fields:
            args.extend(
                get_field_cli_args(
                    subfield, cli_names, parent=field, force_optional=force_optional
                )
            )
        return args
    elif hasattr(field, "choice") and field.choice and field.type.name != "enum":
        args = []
        for choice_field in field.choice:
            # If we have a union or enum, everything deriving from it is optional
            choice_args = get_field_cli_args(
                choice_field, cli_names, parent=field, force_optional=True
            )
            args.extend(choice_args)
        return args
    else:
        arg_type, arg_converter = get_field_cli_type(field, parent=parent)
        if name in cli_names:
            name = cli_names[name]
        return [
            _create_field_arg(
                name, arg_type, arg_converter, field.props, force_optional
            )
        ]


def _create_field_arg(
    name: str, arg_type, arg_converter, props: AnyProps, force_optional: bool
) -> ArgparseArg:
    if arg_type == ty.UUID:  # TODO: Shouldn't we allow UUID?
        arg_type = str
    help_texts = [props.title, props.description]
    arg_help = ": ".join([t for t in help_texts if t is not None])
    arg_opt = f"--{name}" if not props.positional or arg_type is bool else None
    arg = Arg(arg_opt, help=arg_help if arg_help else None, converter=arg_converter)
    default = (
        props.value
        if (force_optional or props.value is not None or not props.required)
        else DEFAULT_PLACEHOLDER
    )
    has_converter = arg_converter is not None and arg_converter not in BASE_TYPES
    ap_arg = get_arg(
        name,
        arg,
        arg_converter if has_converter else arg_type,
        orig_type=arg_type,
        default=default,
        has_converter=has_converter,
        skip_resolve=has_converter,
    )
    ap_arg.help = join_strings(
        arg.help,
        f"({format_type(arg_type)})",
        f"(default: {default})" if default != DEFAULT_PLACEHOLDER else "",
    )
    return ap_arg


def parse_plan(
    schema: RecipeSchema,
    plan: PlanType,
    objects_map: ObjectsMapType,
    get_custom_type: TypeCallbackType,
) -> ty.Tuple[ty.List[str], ty.Dict]:
    # This doesn't deal with defaults or validation at all – we assume that
    # those aspects are handled by the function itself.
    plan = dict(plan)
    args = []
    kwargs: ty.Dict[str, ty.Any] = {}
    plan = resolve_cli_names(plan, schema.cli_names)
    for field in schema.fields:
        value = _parse_field(field, plan, objects_map, get_custom_type)
        if value is UNPARSED and not field.props.required:
            continue
        if value is UNPARSED:  # TODO: improve errors
            raise RecipeProcessingError(f"Could not parse field '{field.name}'", plan)
        if isinstance(value, ty.UUID):
            value = str(value)
        if field.props.positional:
            args.append(value)
        else:
            kwargs[field.name.replace("-", "_")] = value
    return args, kwargs


def _parse_field(
    field: Field,
    plan: PlanType,
    objects_map: ObjectsMapType,
    get_custom_type: TypeCallbackType,
) -> ty.Any:
    """Parse a given schema field using the argument values provided."""
    object_type = field.type.object_type
    if field.type.name == "union":  # try parsing all fields of a union
        maybe_values = []
        for choice in field.choice:
            maybe_value = _parse_field(choice, plan, objects_map, get_custom_type)
            if maybe_value is not UNPARSED:
                maybe_values.append((choice, maybe_value))
        if not maybe_values:  # no union fields could be parsed
            return UNPARSED
        elif len(maybe_values) == 1:  # only one field could be parsed
            return maybe_values[0][1]
        else:  # figure out which field to return
            for maybe_field, maybe_value in maybe_values:
                for field_name in get_field_names(maybe_field):
                    if field_name in plan:
                        return maybe_value
                if maybe_field.name in plan:  # the union choice
                    return maybe_value
    if field.type.name == "optional":  # if value is provided, parse as original type
        maybe_field = field.choice[0]
        maybe_value = _parse_field(maybe_field, plan, objects_map, get_custom_type)
        for field_name in get_field_names(maybe_field):
            if field_name in plan:
                return maybe_value
        if maybe_field.name in plan:
            return maybe_value
        return UNPARSED
    elif object_type is not None and field.name in plan:
        name = plan[field.name]
        if isinstance(name, ty.UUID):
            name = str(name)
        if not isinstance(name, str):
            err = f"Invalid object field '{name}' ({type(name)})"
            raise RecipeProcessingError(err, plan)
        object_data = objects_map.get(object_type, {}).get(name)
        if object_data is None:
            err = f"Can't find data for {object_type} '{name}' in objects map"
            err_info = (
                f"This can happen when running a recipe without a connection to "
                f"the cluster. You can provide a path to a JSON file keyed by "
                f"object type with data to use for named objects via the "
                f"PRODIGY_TEAMS_RECIPES_OBJECTS_PATH environment variable. For example:\n"
                f'{{"{object_type}": {{"{name}": {{"name": "{name}", ...}}}}}}'
            )
            raise RecipeProcessingError(err, err_info)
        assert isinstance(object_data, dict)
        custom_type = get_custom_type(field.type.name)
        keys = {"name", "id", "broker_id", "version", "path", "meta"}
        value = {k: v for k, v in object_data.items() if k in keys}
        return call_custom_type(custom_type, value)
    elif object_type is not None:
        return UNPARSED
    elif field.fields:  # parse subfields
        value = {}
        for subfield in field.fields:
            maybe_value = _parse_field(subfield, plan, objects_map, get_custom_type)
            if maybe_value is UNPARSED and subfield.props.required:
                return UNPARSED
            elif maybe_value is not UNPARSED:
                value[subfield.name.rsplit(".", 1)[1]] = maybe_value
        custom_type = get_custom_type(field.type.name)
        return call_custom_type(custom_type, value)
    elif field.type.name == "list":
        return _parse_list_field(field, plan, objects_map, get_custom_type)
    elif field.name in plan:
        value = plan[field.name]
        custom_type = get_custom_type(field.type.name)
        if custom_type is not None and inspect.isclass(
            custom_type
        ):  # the custom type doesn't have fields
            if value is True:
                # we can receive the choice as bool but it's actually an object
                value = {}
            assert isinstance(value, dict)
            return call_custom_type(custom_type, value)
        return value
    else:
        return UNPARSED


def _parse_list_field(
    field: Field,
    plan: PlanType,
    objects_map: ObjectsMapType,
    get_custom_type: TypeCallbackType,
) -> ty.Any:
    if field.name not in plan:
        return UNPARSED
    list_values = plan[field.name]
    if not isinstance(list_values, list):
        err = f"Received invalid list value for '{field.name}'"
        raise RecipeProcessingError(err, list_values)
    if field.type.args and isinstance(field.type.args[0], models.TypeSchema):
        result = []
        for item in list_values:
            dummy = Field(name=field.name, type=field.type.args[0], props=field.props)
            value = _parse_field(
                dummy, {field.name: item}, objects_map, get_custom_type
            )
            if value is UNPARSED:
                return UNPARSED
            result.append(value)
        return result
    return list_values


def call_custom_type(
    custom_type: ty.Optional[ty.Callable[..., _CustomT]], values: ty.Dict[str, ty.Any]
) -> _CustomT:
    assert custom_type is not None
    values = {key.replace("-", "_"): value for key, value in values.items()}
    try:
        return custom_type(**values)
    except Exception as e:
        raise RecipeProcessingError(
            f"Failed to call custom type {custom_type} with values {values}. Error: {e}"
        ) from e


def resolve_cli_names(
    args: ty.Dict[str, ty.Any], cli_names: ty.Optional[ty.Dict[str, str]]
) -> ty.Dict[str, ty.Any]:
    if not cli_names:
        return args
    inverse_cli_names = {v: k for k, v in cli_names.items()}
    new_args = {}
    for key, value in args.items():
        new_args[inverse_cli_names.get(key, key)] = value
    return new_args
