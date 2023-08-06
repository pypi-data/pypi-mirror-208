from typing import Callable, Optional

from mypy.nodes import (
    AssignmentStmt,
    CallExpr,
    Expression,
    FuncDef,
    NameExpr,
    RefExpr,
    TypeInfo,
)
from mypy.plugin import ClassDefContext, FunctionContext, Plugin
from mypy.types import (
    AnyType,
    CallableType,
    Instance,
    NoneType,
    ProperType,
    Type,
    TypeOfAny,
    UnionType,
    get_proper_type,
)

CHAUSIE_MODULE = "cleanchausie"
CONSTS_MODULE = f"{CHAUSIE_MODULE}.consts"
FIELDS_MODULE = f"{CHAUSIE_MODULE}.fields"
SCHEMA_MODULE = f"{CHAUSIE_MODULE}.schema"
SCHEMA_CLS_MODULE = f"{SCHEMA_MODULE}.Schema"
FIELD_FUNC_MODULE = f"{FIELDS_MODULE}.field.field"
FIELD_CLS_MODULE = f"{FIELDS_MODULE}.field.Field"
NULLABILITY_CLS_MODULE = f"{FIELDS_MODULE}.field.Nullability"
REQUIRED_CLS_MODULE = f"{FIELDS_MODULE}.field.Required"
OMITTABLE_CLS_MODULE = f"{FIELDS_MODULE}.field.Omittable"


def _unwrap_optional_field_type(field_type: Instance) -> ProperType:
    # Field[Optional[str]] -> Field[str]
    # Field[Union[str, int, None]] -> Field[Union[str, int]]
    if (
        isinstance(field_type.args[0], UnionType)
        and NoneType() in field_type.args[0].items
    ):
        non_nonetypes = [
            i for i in field_type.args[0].items if i != NoneType()
        ]
        if len(non_nonetypes) == 1:
            return non_nonetypes[0]
        else:
            return UnionType.make_union(non_nonetypes)
    else:
        return field_type.args[0]


def _infer_type_for_required(
    ctx: FunctionContext, required_expr: Expression
) -> Optional[Type]:
    """Infer a smarter type for `Required` fields.

    Returns None if nothing better could be inferred.
    """
    field_type = get_proper_type(ctx.default_return_type)

    # unwrap any `Optional`'s in the Field[FType]. We'll recalculate that
    # manually here.
    unwrapped_return_type = _unwrap_optional_field_type(field_type)

    # try to infer if we need to add "Optional[X]"
    for arg_name, arg in zip(required_expr.arg_names, required_expr.args):
        if arg_name == "allow_none" and arg.fullname == "builtins.True":
            # Field(nullability=Required(allow_none=True))
            # Change resolved return type to Union[NoneType, X]
            return field_type.copy_modified(
                args=[
                    UnionType(
                        items=[
                            NoneType(),
                            get_proper_type(unwrapped_return_type),
                        ]
                    )
                ]
            )

    # couldn't infer something smarter
    return None


def _infer_type_for_omittable(
    ctx: FunctionContext, omittable_expr: Expression
) -> Type:
    field_type = get_proper_type(ctx.default_return_type)
    # unwrap any `Optional`'s in the Field[FType]. We'll recalculate that
    # manually here.
    unwrapped_return_type = _unwrap_optional_field_type(field_type)

    allow_none: bool = True
    omitted_type: Optional[Type] = None
    for arg_name, arg in zip(omittable_expr.arg_names, omittable_expr.args):
        if arg_name == "allow_none" and arg.fullname == "builtins.False":
            allow_none = False
        if arg_name == "omitted_value" and omitted_type is None:
            omitted_type = ctx.api.expr_checker.accept(arg)
        if arg_name == "omitted_value_factory":
            if not isinstance(arg, RefExpr):
                # only supports named functions + classes.
                # Fall back to `Any` (for things like lambda
                # expressions)
                omitted_type = AnyType(
                    type_of_any=TypeOfAny.implementation_artifact
                )
            elif isinstance(arg.node, FuncDef):
                omitted_type = arg.node.type.ret_type
            elif isinstance(arg.node, TypeInfo):
                omitted_type = Instance(typ=arg.node, args=[])
            else:
                # not sure what other ref type would be here
                ctx.api.fail("Unknown arg type within omitted value factory")

    union_items = [unwrapped_return_type]
    if allow_none and NoneType() not in union_items:
        union_items.append(NoneType())
    if omitted_type is None:
        omitted_type = (
            ctx.api.modules[CONSTS_MODULE].names["omitted"].node.type
        )
    if (
        isinstance(omitted_type, Instance)
        and not any(
            omitted_type.type == i.type
            for i in union_items
            if isinstance(i, Instance)
        )
    ) or (
        not isinstance(omitted_type, Instance)
        and omitted_type not in union_items
    ):
        union_items.append(omitted_type)

    if len(union_items) > 1:
        return field_type.copy_modified(args=[UnionType(items=union_items)])
    else:
        return field_type.copy_modified(args=[union_items[0]])


def func_hook(ctx: FunctionContext) -> Type:
    field_type = get_proper_type(ctx.default_return_type)

    # TODO properly support decorator syntax
    if isinstance(field_type, CallableType):
        return ctx.default_return_type

    for n, t, v in zip(ctx.arg_names, ctx.arg_types, ctx.args):
        if n == ["nullability"]:
            if isinstance(v[0], NameExpr):
                # Usage like: field(..., nullability=my_nullability)
                # Can't infer much from this without adding type args to
                # the Nullability subclasses.
                continue
            # infer:
            #  * X
            #  * Union[NoneType, X]
            #  * Union[OMITTED_TYPE, X]
            #  * Union[OMITTED_TYPE, NoneType, X]
            # Note that `OMITTED_TYPE` will be the type of the
            # `omitted_value` (or the return type of
            # `omitted_value_factory`) if present, falling back to the
            # default `OMITTED` class
            if t[0].type.fullname == NULLABILITY_CLS_MODULE:
                # can't do much here, need a specific subclass
                pass
            elif t[0].type.fullname == REQUIRED_CLS_MODULE:
                if inferred := _infer_type_for_required(ctx, v[0]):
                    return inferred
            elif t[0].type.fullname == OMITTABLE_CLS_MODULE:
                return _infer_type_for_omittable(ctx, v[0])
            else:
                ctx.api.fail("Unknown nullability class type")

    # unwrap Optional by default: `Field[Optional[str]] -> Field[str]`
    return field_type.copy_modified(
        args=[_unwrap_optional_field_type(field_type)]
    )


def base_class_hook(ctx: ClassDefContext) -> None:
    field_cls = ctx.api.lookup_fully_qualified(FIELD_CLS_MODULE)
    for defn in ctx.cls.defs.body:
        # look for defs like: `attrib: str = field(StrField(...), ...)`
        # convert them to:    `attrib: Field[str] = field(StrField(...), ...)`
        if (
            isinstance(defn, AssignmentStmt)
            and len(defn.lvalues) == 1
            and isinstance(defn.lvalues[0], NameExpr)
            and isinstance(defn.rvalue, CallExpr)
            and defn.rvalue.callee.fullname.startswith(FIELDS_MODULE)
        ):
            name = defn.lvalues[0].name
            namedef = ctx.cls.info.names.get(name)
            if not namedef:
                continue
            if isinstance(namedef.type, UnionType) or (
                isinstance(namedef.type, Instance)
                and namedef.type.type != field_cls.node
            ):
                # mutate the parsed class definition to add the Field wrapper
                namedef.node.type = Instance(
                    typ=field_cls.node, args=[defn.type]
                )

    return None


class ChausiePlugin(Plugin):
    def get_function_hook(
        self, fullname: str
    ) -> Optional[Callable[[FunctionContext], Type]]:
        if fullname == FIELD_FUNC_MODULE:
            return func_hook
        return None

    def get_base_class_hook(
        self, fullname: str
    ) -> Optional[Callable[[ClassDefContext], None]]:
        if fullname == SCHEMA_CLS_MODULE:
            return base_class_hook
        return None


def plugin(version: str):
    return ChausiePlugin
