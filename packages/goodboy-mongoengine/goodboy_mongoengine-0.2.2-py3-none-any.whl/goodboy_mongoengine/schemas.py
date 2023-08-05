from typing import Any, Optional

import goodboy as gb
from bson import ObjectId
from bson.errors import InvalidId
from goodboy.schema import Rule

from goodboy_mongoengine.messages import DEFAULT_MESSAGES


class ObjectIdSchema(gb.SchemaWithUtils):
    """
    Accept ``bson.ObjectId`` values.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    """

    def __init__(
        self,
        *,
        allow_none: bool = False,
        messages: gb.MessageCollectionType = DEFAULT_MESSAGES,
        rules: list[Rule] = [],
    ) -> None:
        super().__init__(allow_none=allow_none, messages=messages, rules=rules)

    def _validate(
        self, value: Any, typecast: bool, context: dict[str, Any] = {}
    ) -> tuple[Optional[ObjectId], list[gb.Error]]:
        if not isinstance(value, ObjectId):
            return None, [
                self._error("unexpected_type", {"expected_type": gb.type_name("id")})
            ]

        value, rule_errors = self._call_rules(value, typecast, context)

        return value, rule_errors

    def _typecast(
        self, input: Any, context: dict[str, Any] = {}
    ) -> tuple[Optional[bool], list[gb.Error]]:
        if isinstance(input, ObjectId):
            return input, []

        if isinstance(input, str):
            try:
                return ObjectId(input)
            except InvalidId:
                pass

        return None, [
            self._error("unexpected_type", {"expected_type": gb.type_name("id")})
        ]
