from typing import Any, Mapping, Type

import goodboy as gb
import mongoengine as me

from goodboy_mongoengine.document_key import DocumentKeyBuilder, document_key_builder
from goodboy_mongoengine.field import FieldBuilder, field_builder
from goodboy_mongoengine.messages import DEFAULT_MESSAGES


class DocumentInstanceProxyKeyError(Exception):
    """
    Exception used in DocumentInstanceProxy instead of standard KeyError, to avoid
    accidental catching KeyError exception from an document instance property.
    """

    pass


class DocumentInstanceProxy(Mapping[str, Any]):
    def __init__(
        self,
        document_instance: me.Document,
        key_names: list[str],
        override_values: dict,
    ):
        self._document_instance = document_instance
        self._key_names = key_names
        self._override_values = override_values

    def get(self, key, default=None):
        try:
            return self._getitem(key, default)
        except DocumentInstanceProxyKeyError:
            return default

    def __contains__(self, key):
        return key in self._key_names

    def __getitem__(self, key):
        try:
            return self._getitem(key, None)
        except DocumentInstanceProxyKeyError:
            raise KeyError(key)

    def __len__(self):
        return len(self._key_names)

    def __iter__(self):
        return iter(self._key_names)

    def _getitem(self, key, default):
        if key not in self._key_names:
            raise DocumentInstanceProxyKeyError()

        if key in self._override_values:
            return self._override_values[key]

        if self._document_instance:
            return getattr(self._document_instance, key, default)

        return default


class DocumentSchemaError(Exception):
    pass


class DocumentSchema(gb.Schema, gb.SchemaErrorMixin):
    def __init__(
        self,
        document_class: Type[me.Document],
        fields: list[gb.Key] = [],
        field_names: list[str] = [],
        field_builder: FieldBuilder = field_builder,
        document_key_builder: DocumentKeyBuilder = document_key_builder,
        messages: gb.MessageCollectionType = DEFAULT_MESSAGES,
    ):
        super().__init__()

        self._document_class = document_class
        self._messages = messages

        self._fields = fields + field_builder.build(document_class, field_names)
        self._document_keys = document_key_builder.build(
            document_class, self._fields, messages
        )
        self._document_key_names = [dk.name for dk in self._document_keys]

    def __call__(self, value, *, typecast=False, context: dict = {}):
        if not isinstance(value, dict):
            error = self._error(
                "unexpected_type", {"expected_type": gb.type_name("dict")}
            )

            raise gb.SchemaError([error])

        instance: me.Document | None = context.get("document_instance")

        value, errors = self._validate(value, typecast, context, instance)

        if errors:
            raise gb.SchemaError(errors)

        return value

    def _validate(
        self,
        value: dict,
        typecast: bool,
        context: dict,
        instance: me.Document | None = None,
    ):
        result: dict = {}

        key_errors = {}
        value_errors = {}

        unknown_keys = list(value.keys())

        instance = context.get("document_instance")
        instance_proxy = DocumentInstanceProxy(
            instance, self._document_key_names, value
        )

        for document_key in self._document_keys:
            if not document_key.predicate_result(instance_proxy):
                continue

            if document_key.name in unknown_keys:
                unknown_keys.remove(document_key.name)

                try:
                    key_value = document_key.validate(
                        value[document_key.name],
                        typecast,
                        context,
                        instance,
                    )
                except gb.SchemaError as e:
                    value_errors[document_key.name] = e.errors
                else:
                    result[document_key.result_key_name] = key_value
            elif instance is None:
                if document_key.required:
                    key_errors[document_key.name] = [self._error("required_key")]
                elif document_key.default is not None:
                    if callable(document_key.default):
                        result[document_key.result_key_name] = document_key.default()
                    else:
                        result[document_key.result_key_name] = document_key.default

        errors: list[gb.Error] = []

        for key_name in unknown_keys:
            key_errors[key_name] = [self._error("unknown_key")]

        if key_errors:
            errors.append(self._error("key_errors", nested_errors=key_errors))

        if value_errors:
            errors.append(self._error("value_errors", nested_errors=value_errors))

        return result, errors
