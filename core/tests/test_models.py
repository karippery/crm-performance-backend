import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from core.models import Address, AppUser, CustomerRelationship
from core.tests.conftest import AddressFactory, AppUserFactory, CustomerRelationshipFactory


@pytest.mark.django_db
class TestAddressModel:
    """Test cases for Address model."""

    def test_address_creation(self):
        """Test basic address creation."""
        address = AddressFactory()
        assert address.id is not None
        assert len(address.street) >= 2
        assert len(address.city) >= 2
        assert len(address.country) >= 2

    def test_address_str_representation(self):
        """Test address string representation."""
        address = AddressFactory(
            street="Main Street",
            street_number="123",
            city="Berlin",
            country="Germany"
        )
        expected = "Main Street 123, Berlin, Germany"
        assert str(address) == expected

    def test_address_validation_min_length(self):
        """Test address field minimum length validation."""
        with pytest.raises(ValidationError):
            address = Address(
                street="A",  # Too short
                street_number="1",
                city_code="12345",
                city="Berlin",
                country="Germany"
            )
            address.full_clean()

    def test_address_indexes(self):
        """Test that indexes are properly defined."""
        # This test ensures the model definition includes expected indexes
        assert hasattr(Address._meta, 'indexes')
        index_fields = [idx.fields for idx in Address._meta.indexes]
        assert ['city_code'] in index_fields
        assert ['city', 'country'] in index_fields


@pytest.mark.django_db
class TestAppUserModel:
    """Test cases for AppUser model."""

    def test_user_creation(self, sample_address):
        """Test basic user creation."""
        user = AppUserFactory(address=sample_address)
        assert user.id is not None
        assert user.address == sample_address
        assert user.customer_id is not None

    def test_user_str_representation(self, sample_address):
        """Test user string representation."""
        user = AppUserFactory(
            first_name="John",
            last_name="Doe",
            address=sample_address
        )
        assert str(user) == "John Doe"

    def test_unique_customer_id(self, sample_address):
        """Test customer_id uniqueness constraint."""
        customer_id = "CUST123456"
        AppUserFactory(customer_id=customer_id, address=sample_address)
        
        with pytest.raises(IntegrityError):
            AppUserFactory(customer_id=customer_id, address=sample_address)

    def test_birthday_validation_future_date(self, sample_address):
        """Test birthday cannot be in the future."""
        future_date = date.today() + timedelta(days=1)
        
        with pytest.raises(ValidationError):
            user = AppUser(
                first_name="John",
                last_name="Doe",
                gender="Male",
                customer_id="CUST123456",
                address=sample_address,
                birthday=future_date
            )
            user.full_clean()

    def test_birthday_validation_too_old(self, sample_address):
        """Test birthday cannot be before 1900."""
        old_date = date(1899, 12, 31)
        
        with pytest.raises(ValidationError):
            user = AppUser(
                first_name="John",
                last_name="Doe",
                gender="Male",
                customer_id="CUST123456",
                address=sample_address,
                birthday=old_date
            )
            user.full_clean()

    def test_valid_birthday(self, sample_address):
        """Test valid birthday passes validation."""
        valid_date = date(1990, 5, 15)
        user = AppUser(
            first_name="John",
            last_name="Doe",
            gender="Male",
            customer_id="CUST123456",
            address=sample_address,
            birthday=valid_date
        )
        user.full_clean()  # Should not raise

    def test_gender_choices(self, sample_address):
        """Test gender field choices."""
        valid_genders = ["Male", "Female", "Other", "Prefer not to say"]
        
        for gender in valid_genders:
            user = AppUserFactory(gender=gender[:20], address=sample_address)
            assert user.gender == gender

    def test_name_min_length_validation(self, sample_address):
        """Test first_name and last_name minimum length validation."""
        with pytest.raises(ValidationError):
            user = AppUser(
                first_name="A",  # Too short
                last_name="Doe",
                gender="Male",
                customer_id="CUST123456",
                address=sample_address
            )
            user.full_clean()

    def test_ordering(self):
        """Test model ordering by -created."""
        user1 = AppUserFactory()
        user2 = AppUserFactory()
        
        users = list(AppUser.objects.all())
        assert users[0].created >= users[1].created


@pytest.mark.django_db
class TestCustomerRelationshipModel:
    """Test cases for CustomerRelationship model."""

    def test_relationship_creation(self, sample_user):
        """Test basic relationship creation."""
        relationship = CustomerRelationshipFactory(appuser=sample_user)
        assert relationship.id is not None
        assert relationship.appuser == sample_user

    def test_relationship_str_representation(self, sample_user):
        """Test relationship string representation."""
        relationship = CustomerRelationshipFactory(
            appuser=sample_user,
            points=500
        )
        expected = f"User: {sample_user.id}, Points: 500"
        assert str(relationship) == expected

    def test_unique_together_constraint(self, sample_user):
        """Test unique_together constraint on appuser and created."""
        created_time = timezone.now()
        CustomerRelationshipFactory(appuser=sample_user, created=created_time)
        
        with pytest.raises(IntegrityError):
            CustomerRelationshipFactory(appuser=sample_user, created=created_time)

    def test_cascade_delete(self, sample_user):
        """Test cascade delete when user is deleted."""
        relationship = CustomerRelationshipFactory(appuser=sample_user)
        relationship_id = relationship.id
        
        sample_user.delete()
        
        assert not CustomerRelationship.objects.filter(id=relationship_id).exists()