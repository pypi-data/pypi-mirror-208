

import dataclasses
from typing import Callable, Literal, Mapping, List, Optional, Any, Sequence, Type, TypeVar, Union
from strawberry import BasePermission, Private, interface
from strawberry.field import StrawberryField
from strawberry.extensions import FieldExtension
from strawberry.annotation import StrawberryAnnotation


T = TypeVar("T")


class Field(StrawberryField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self,  *args, **kwargs) -> StrawberryField:
        resolver = args[0]
        return super().__call__(resolver)


def field(
    resolver: Optional[Callable[[], T]] = None,
    *,
    name: Optional[str] = None,
    is_subscription: bool = False,
    description: Optional[str] = None,
    permission_classes: Optional[List[Type[BasePermission]]] = None,
    deprecation_reason: Optional[str] = None,
    default: Any = dataclasses.MISSING,
    default_factory: Union[Callable[..., object],
                           object] = dataclasses.MISSING,
    metadata: Optional[Mapping[Any, Any]] = None,
    directives: Optional[Sequence[object]] = (),
    extensions: Optional[List[FieldExtension]] = None,
    graphql_type: Optional[Any] = None,
    # This init parameter is used by PyRight to determine whether this field
    # is added in the constructor or not. It is not used to change
    # any behavior at the moment.
    init: Literal[True, False, None] = None,
) -> T:
    """Annotates a method or property as a GraphQL field.

    This is normally used inside a type declaration:

    >>> @strawberry.type:
    >>> class X:
    >>>     field_abc: str = strawberry.field(description="ABC")

    >>>     @strawberry.field(description="ABC")
    >>>     def field_with_resolver(self) -> str:
    >>>         return "abc"

    it can be used both as decorator and as a normal function.
    """

    type_annotation = StrawberryAnnotation.from_annotation(graphql_type)

    field_ = Field(
        python_name=None,
        graphql_name=name,
        type_annotation=type_annotation,
        description=description,
        is_subscription=is_subscription,
        permission_classes=permission_classes or [],
        deprecation_reason=deprecation_reason,
        default=default,
        default_factory=default_factory,
        metadata=metadata,
        directives=directives or (),
        extensions=extensions or [],
    )

    if resolver:
        assert init is not True, "Can't set init as True when passing a resolver."
        return field_(resolver)
    return field_

@interface
class Node:
    _id: Private[str]
    type: Private[str] = "node"

    @field
    def id(self) -> str:
        return '{}:{}'.format(self.type, self._id)

    @field
    def const(self, t: str) -> str:
        return t