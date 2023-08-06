from NEMO.serializers import ModelSerializer
from NEMO.views.api import ModelViewSet
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.fields import CharField

from NEMO_billing.models import CustomCharge


class CustomChargeSerializer(FlexFieldsModelSerializer, ModelSerializer):
    class Meta:
        model = CustomCharge
        fields = "__all__"
        expandable_fields = {
            "customer": "NEMO.serializers.UserSerializer",
            "creator": "NEMO.serializers.UserSerializer",
            "project": "NEMO.serializers.ProjectSerializer",
        }

    customer_name = CharField(source="customer.get_name")
    creator_name = CharField(source="creator.get_name")


class CustomChargeViewSet(ModelViewSet):
    filename = "custom_charges"
    queryset = CustomCharge.objects.all()
    serializer_class = CustomChargeSerializer
    filterset_fields = {
        "name": ["exact"],
        "customer": ["exact", "in"],
        "creator": ["exact", "in"],
        "project": ["exact", "in"],
        "date": ["exact", "month", "year", "gte", "gt", "lte", "lt"],
        "amount": ["exact", "gte", "gt", "lte", "lt"],
        "core_facility": ["exact", "in", "isnull"],
    }
