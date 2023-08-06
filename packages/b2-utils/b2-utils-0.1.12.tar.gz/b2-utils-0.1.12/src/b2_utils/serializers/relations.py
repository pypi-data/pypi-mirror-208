from rest_framework import fields as _fields
from rest_framework import relations as _relations

__all__ = [
    "PrimaryKeyRelatedFieldWithSerializer",
    "DynamicPrimaryKeyRelatedFieldWithSerializer",
]


class PrimaryKeyRelatedFieldWithSerializer(_relations.PrimaryKeyRelatedField):
    def __init__(self, representation_serializer, write_protected=False, **kwargs):
        self.representation_serializer = representation_serializer
        self.write_protected = write_protected

        super().__init__(**kwargs)

    def to_representation(self, value):
        if callable(value):
            return self.representation_serializer(
                value.all(),
                context=self.context,
                many=True,
            ).data

        instance = self.queryset.get(pk=value.pk)

        return self.representation_serializer(instance, context=self.context).data

    def validate_empty_values(self, data):
        if self.write_protected:
            raise _fields.SkipField

        return super().validate_empty_values(data)


class DynamicPrimaryKeyRelatedFieldWithSerializer(PrimaryKeyRelatedFieldWithSerializer):
    """
    Work like PrimaryKeyRelatedFieldWithSerializer but allow to specify fields to be serialized
    and the representation_serializer must be have DynamicFieldsSerializer as parent
    """

    def __init__(self, fields=None, **kwargs):
        self.representation_fields = fields

        super().__init__(**kwargs)

    def to_representation(self, value):
        kwargs = {}
        if callable(value):
            kwargs = {
                "instance": value.all(),
                "many": True,
            }
        else:
            kwargs["instance"] = self.queryset.get(pk=value.pk)

        if self.representation_fields:
            kwargs["fields"] = self.representation_fields

        return self.representation_serializer(**kwargs).data


class DynamicFieldsSerializer:
    def __init__(self, *args, **kwargs) -> None:
        fields = kwargs.pop("fields", None)

        super().__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
