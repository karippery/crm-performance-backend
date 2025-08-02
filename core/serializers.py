from rest_framework import serializers
from core.models import AppUser, Address, CustomerRelationship


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "street",
            "street_number",
            "city_code",
            "city",
            "country"
        ]


class CustomerRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerRelationship
        fields = [
            "points",
            "created",
            "last_activity"
        ]


class AppUserSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    relationships = CustomerRelationshipSerializer(many=True, read_only=True)

    class Meta:
        model = AppUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "customer_id",
            "phone_number",
            "created",
            "birthday",
            "last_updated",
            "address",
            "relationships"
        ]
