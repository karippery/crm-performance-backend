import pytest
from core.serializers import AddressSerializer, AppUserSerializer, CustomerRelationshipSerializer
from core.tests.conftest import AddressFactory, CustomerRelationshipFactory


@pytest.mark.django_db
class TestAddressSerializer:
    """Test cases for AddressSerializer."""

    def test_address_serialization(self):
        """Test address serialization."""
        address = AddressFactory()
        serializer = AddressSerializer(address)
        
        expected_fields = [
            'street', 'street_number', 'city_code', 'city', 'country'
        ]
        
        assert set(serializer.data.keys()) == set(expected_fields)
        assert serializer.data['street'] == address.street
        assert serializer.data['city'] == address.city

    def test_address_deserialization(self):
        """Test address deserialization."""
        data = {
            'street': 'Main Street',
            'street_number': '123',
            'city_code': '12345',
            'city': 'Berlin',
            'country': 'Germany'
        }
        
        serializer = AddressSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestCustomerRelationshipSerializer:
    """Test cases for CustomerRelationshipSerializer."""

    def test_relationship_serialization(self, sample_user):
        """Test relationship serialization."""
        relationship = CustomerRelationshipFactory(appuser=sample_user)
        serializer = CustomerRelationshipSerializer(relationship)
        
        expected_fields = ['points', 'created', 'last_activity']
        
        assert set(serializer.data.keys()) == set(expected_fields)
        assert serializer.data['points'] == relationship.points


@pytest.mark.django_db
class TestAppUserSerializer:
    """Test cases for AppUserSerializer."""

    def test_user_serialization_without_relationships(self, sample_user):
        """Test user serialization without relationships."""
        serializer = AppUserSerializer(sample_user)
        
        expected_fields = [
            'id', 'first_name', 'last_name', 'gender', 'customer_id',
            'phone_number', 'created', 'birthday', 'last_updated',
            'address', 'relationships'
        ]
        
        assert set(serializer.data.keys()) == set(expected_fields)
        assert serializer.data['first_name'] == sample_user.first_name
        assert serializer.data['relationships'] == []

    def test_user_serialization_with_relationships(self, sample_user):
        """Test user serialization with relationships."""
        relationship = CustomerRelationshipFactory(appuser=sample_user)
        serializer = AppUserSerializer(sample_user)
        
        assert len(serializer.data['relationships']) == 1
        assert serializer.data['relationships'][0]['points'] == relationship.points

    def test_nested_address_serialization(self, sample_user):
        """Test nested address serialization."""
        serializer = AppUserSerializer(sample_user)
        
        address_data = serializer.data['address']
        assert address_data['street'] == sample_user.address.street
        assert address_data['city'] == sample_user.address.city