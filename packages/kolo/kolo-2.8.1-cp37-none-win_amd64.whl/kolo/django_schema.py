from decimal import Decimal
from typing import Any, Dict


def get_schema():
    from django.apps import apps

    schema = {}
    for config in apps.get_app_configs():
        for model in config.get_models():
            schema[model._meta.db_table] = model_schema(model)
    return schema


def model_schema(model):
    fields: Dict[str, Any] = {}
    schema = {
        "model_module": model.__module__,
        "model_name": model.__qualname__,
        "fields": fields,
    }
    for field in model._meta.get_fields():
        try:
            column = field.column
            field.attname
        except AttributeError:
            # `ForeignObjectRel` or `GenericForeignKey`
            continue

        if column is None:
            # `GenericRelation`
            continue
        fields[column] = field_schema(field)
    return schema


def field_schema(field):
    from django.db.models.fields import NOT_PROVIDED

    field_class = type(field)
    schema = {
        "field_name": field.attname,
        "null": field.null,
        "primary_key": field.primary_key,
        "is_relation": field.is_relation,
        "django_field": f"{field_class.__module__}.{field_class.__qualname__}",
    }
    if field.default is not NOT_PROVIDED and not callable(field.default):
        schema["default"] = field_default(field.default)
    if hasattr(field, "auto_now"):
        schema["auto_now"] = field.auto_now
        schema["auto_now_add"] = field.auto_now_add
    if field.is_relation:
        schema["related_model"] = field.related_model._meta.db_table

    return schema


def field_default(default):
    from django.db.models import Choices

    if isinstance(default, Choices):
        default = {
            "value": default._value_,
            "name": default._name_,
            "label": default.label,
            "choices_name": type(default).__qualname__,
            "choices_module": type(default).__module__,
        }
    elif isinstance(default, Decimal):
        default = {
            "value": str(default),
            "type": "Decimal",
        }
    else:
        default = {"value": default}
    return default
