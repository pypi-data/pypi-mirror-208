from typing import Any, Dict, List, Protocol, Union
from psychonaut.lexicon.constants import MODULE_PREFIX

from psychonaut.lexicon.ctx import GenCtx
from psychonaut.lexicon.util import camel_to_class_name, camel_to_snake
from .types import (
    LexArray,
    LexInteger,
    LexObject,
    LexString,
    LexBoolean,
    LexXrpcParameters,
)


class FieldDef(Protocol):
    name: str
    type: str
    required: bool
    opts: Dict[str, Any]


def generate_pydantic_fields(
    ctx: GenCtx, params: Union[LexXrpcParameters, LexObject]
) -> List[str]:
    # Needs:
    # .required
    # .properties
    #
    # compiles: LexObject
    # compiles: LexXrpcParameters
    if not params or not params.properties:
        return []

    required_fields = set(params.required or [])

    return [
        _generate_field(ctx, prop_name, prop_name in required_fields, prop_type)
        for prop_name, prop_type in params.properties.items()
    ]


_lex_type_to_pydantic_type = {
    "string": "str",
    "integer": "int",
    "boolean": "bool",
}


def _consistent_opts_str(opts: Dict[str, Any]) -> str:
    alphabetical_opts = sorted(opts.items(), key=lambda x: x[0])
    opts_str = ", ".join(f"{k}={repr(v)}" for k, v in alphabetical_opts)
    return opts_str


def _build_expanded(
    pytype: str, required: bool, opts: Dict[str, Any], name: str
) -> str:
    src = ""

    if not required and "default" not in opts:
        opts["default"] = None

    opts_str = _consistent_opts_str(opts)

    opts_params = ""
    if opts_str:
        opts_params = f", {opts_str}"

    if required:
        if "default" not in opts:
            src = f"{name}: {pytype} = Field(...{opts_params})"
        else:
            src = f"{name}: {pytype} = Field({opts_str})"
    else:
        src = f"{name}: Optional[{pytype}] = Field({opts_str})"

    return src


def _generate_integer_field(name: str, required: bool, props: LexInteger) -> str:
    """
    Generate the source string for a pydantic field for an integer type.
    """
    opts = {}

    if props.minimum is not None:
        opts["ge"] = props.minimum
    if props.maximum is not None:
        opts["le"] = props.maximum
    if props.description is not None:
        opts["description"] = props.description
    if props.default is not None:
        opts["default"] = props.default

    assert props.const is None, "const not implemented"
    assert props.enum is None, "enum not implemented"

    s = _build_expanded("int", required, opts, name)

    return s


def _generate_bool_field(name: str, required: bool, props: LexBoolean) -> str:
    opts = {}

    if props.default is not None:
        opts["default"] = props.default

    if props.description is not None:
        opts["description"] = props.description

    if name == "validate":
        # Pydantic uses 'validate' don't shadow it'
        name = "validate_flag"
        opts["alias"] = "validate"

    # assert props.const is None, "const not implemented" TODO

    return _build_expanded("bool", required, opts, name)


class Symbol:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


def _generate_str_field(
    ctx: GenCtx, name: str, required: bool, props: LexString
) -> str:
    opts = {}

    if props.default is not None:
        opts["default"] = props.default
    if props.description is not None:
        opts["description"] = props.description
    if props.max_length is not None:
        opts["max_length"] = props.max_length

    assert props.const is None, "const not implemented"
    assert props.enum is None, "enum not implemented"
    # assert props.min_graphemes is None, "min_graphemes not implemented"
    # assert props.max_graphemes is None, "max_graphemes not implemented"

    # I don't think these are enforced like an enum
    if props.known_values:
        opts["known_values"] = props.known_values

    if props.format:
        opts["pre"] = True
        validator = _add_imports_and_get_validator(ctx, props.format)
        opts["validator"] = validator

    return _build_expanded("str", required, opts, name)


def _add_imports_and_get_validator(ctx: GenCtx, fmt: str) -> Symbol:
    if fmt == "cid":
        ctx.imports["psychonaut.lexicon.formats"].add("validate_cid")
        return Symbol("validate_cid")
    elif fmt == "nsid":
        ctx.imports["psychonaut.lexicon.formats"].add("validate_nsid")
        return Symbol("validate_nsid")
    elif fmt == "did":
        ctx.imports["psychonaut.lexicon.formats"].add("validate_did")
        return Symbol("validate_did")
    elif fmt == "handle":
        ctx.imports["psychonaut.lexicon.formats"].add("validate_handle")
        return Symbol("validate_handle")
    elif fmt == "at-identifier":
        ctx.imports["psychonaut.lexicon.formats"].add("validate_at_identifier")
        return Symbol("validate_at_identifier")
    elif fmt == "at-uri":
        ctx.imports["psychonaut.lexicon.formats"].add("validate_at_uri")
        return Symbol("validate_at_uri")
    elif fmt == "datetime":
        ctx.imports["psychonaut.lexicon.formats"].add("validate_datetime")
        return Symbol("validate_datetime")
    elif fmt == "uri":
        ctx.imports["psychonaut.lexicon.formats"].add("validate_uri")
        return Symbol("validate_uri")
    else:
        assert False, f"Unknown format: {fmt}"


def _generate_array_field(
    ctx: GenCtx, name: str, required: bool, props: LexArray
) -> str:
    ctx.imports["typing"].add("List")
    ctx.imports["typing"].add("Optional")  # TODO: fix

    opts = {}

    if props.description is not None:
        opts["description"] = props.description

    t = Symbol(f"List[{_lex_type_to_pydantic_type.get(props.items.type, 'Any')}]")

    if props.min_length is not None:
        opts["min_items"] = props.min_length
    if props.max_length is not None:
        opts["max_items"] = props.max_length

    for unimp in ["const", "enum", "known_values", "min_graphemes", "max_graphemes"]:
        if hasattr(props.items, unimp) and getattr(props.items, unimp) is not None:
            assert False, f"{unimp} not implemented"

    if hasattr(props.items, "format") and props.items.format is not None:
        opts["pre"] = True
        underlying_validator = _add_imports_and_get_validator(ctx, props.items.format)
        ctx.imports["psychonaut.lexicon.formats"].add("validate_array")
        opts["validator"] = Symbol(f"validate_array({underlying_validator})")

    return _build_expanded(t, required, opts, name)


def _generate_generic_field(name: str, required: bool, props: Dict[str, Any]) -> str:
    t = _lex_type_to_pydantic_type.get(props.type, "Any")

    if required:
        return f"{name}: {t}"
    else:
        return f"{name}: Optional[{t}] = None"


def _generate_field(
    ctx: GenCtx, name: str, required: bool, props: Dict[str, Any]
) -> str:
    type_ = props.type

    if type_ == "array" and props.items.type == "ref":
        # print(f"Ref to any arr kludge: {ctx.input_path} {name}")
        # print(">>>>>>>>>>>>>>>>>>>>>>", ctx, name, props)
        type_ = "Any"

    if not required:
        ctx.imports["typing"].add("Optional")

    if type_ == "ref":
        return _generate_ref_field(ctx, name, required, props)
    if type_ == "integer":
        return _generate_integer_field(name, required, props)
    elif type_ == "string":
        return _generate_str_field(ctx, name, required, props)
    elif type_ == "boolean":
        return _generate_bool_field(name, required, props)
    elif type_ == "array":
        return _generate_array_field(ctx, name, required, props)
    else:
        print(f"Unknown type: {type_}")
        ctx.imports["typing"].add("Any")
        return _generate_generic_field(name, required, props)


def _generate_ref_field(
    ctx: GenCtx, name: str, required: bool, props: Dict[str, Any]
) -> str:
    ref_class = ""
    if "#" in props.ref:
        if props.ref.startswith("#"):
            ref_class = camel_to_class_name(props.ref[1:])
        elif len(parts := props.ref.split("#")) > 1:
            module = camel_to_snake(parts[0])
            ref_class = camel_to_class_name(parts[1])
            if module != ctx.common_xrpc_id:
                print("YYYYYY", props.ref, module, parts, ctx.common_xrpc_id)
                ctx.imports[MODULE_PREFIX + module].add(camel_to_class_name(parts[-1]))
    else:
        # Assume it's importing the main class at that path
        parts = props.ref.split(".")
        module = MODULE_PREFIX + camel_to_snake(props.ref)
        ref_class = camel_to_class_name(parts[-1])

        ctx.imports[module].add(camel_to_class_name(parts[-1]))

        print("YYY", props.ref, module, ref_class)

        ref_class = camel_to_class_name(props.ref.split(".")[-1])

    ref_class = camel_to_class_name(ref_class)
    if required:
        return f"{name}: {ref_class}"
    else:
        return f"{name}: Optional[{ref_class}] = None"


# def _generate_ref_field(ctx: GenCtx, name: str, required: bool, props: Dict[str, Any]) -> str:
