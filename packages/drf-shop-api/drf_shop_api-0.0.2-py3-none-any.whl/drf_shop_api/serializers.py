from django.db.models.fields.files import FieldFile
from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject

from drf_shop_api.models import Currency, ShippingMethod


class ListSerializerMixin:
    """Use this mixin to be able to define list_serializer_class that
    will be used only for list action"""

    list_serializer_class = None
    serializer_class = None

    list_queryset = None
    queryset = None

    def get_serializer_class(self):
        assert self.list_serializer_class, "Use must set 'list_serializer_class' in order to use ListSerializerMixin"
        if self.action == "list":
            return self.list_serializer_class
        else:
            return super().get_serializer_class()

    def get_queryset(self):
        if self.action == "list" and self.list_queryset is not None:
            return self.list_queryset
        else:
            return super().get_queryset()


class ModelFileSerializer(serializers.ModelSerializer):
    """Parent serializer for ones that have models with File fields.
    This overrides default behaviour and fix bug when serialization is
    broken when file is absent
    """

    def to_representation(self, instance):
        ret = {}
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            # Here we check not for is None but just
            # for ``not check_for_none`` allowing Python + that Django
            # ImageFieldFile to resolve the condition
            if isinstance(attribute, FieldFile) and not check_for_none:
                ret[field.field_name] = None
            elif check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class BaseCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ("title",)


class BaseShippingMethodSerializer(ModelFileSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ShippingMethod
        fields = ("id", "title", "logo")
