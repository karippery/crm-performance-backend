import random
import pytest
from datetime import date, datetime, timedelta
from django.test import Client
from django.utils import timezone
from django.core.cache import cache
from rest_framework.test import APIClient
from core.models import Address, AppUser, CustomerRelationship
import factory
from factory.django import DjangoModelFactory
from factory import fuzzy


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    street = factory.Faker('street_name')
    street_number = factory.Faker('building_number')
    city_code = factory.Faker('postcode')
    city = factory.Faker('city')
    country = factory.Faker('country')


class AppUserFactory(DjangoModelFactory):
    class Meta:
        model = AppUser

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    gender = factory.LazyAttribute(
        lambda x: random.choice(['Male', 'Female', 'Other', 'Prefer not to say'])[:20]
    )
    customer_id = factory.Sequence(lambda n: f'CUST{n:06d}')
    phone_number = factory.LazyAttribute(
        lambda _: f"+{random.randint(1, 9)}{random.randint(1000000000, 9999999999)}"
    )
    address = factory.SubFactory(AddressFactory)
    birthday = factory.Faker(
        'date_between',
        start_date=date(1950, 1, 1),
        end_date=date(2005, 12, 31)
    )
    created = factory.LazyFunction(timezone.now)


class CustomerRelationshipFactory(DjangoModelFactory):
    class Meta:
        model = CustomerRelationship

    appuser = factory.SubFactory(AppUserFactory)
    points = factory.Faker('random_int', min=0, max=10000)
    created = factory.LazyFunction(timezone.now)
    last_activity = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=factory.Faker('random_int', min=1, max=30).evaluate(None, None, {'locale': None}))
    )


@pytest.fixture
def api_client():
    """Provides DRF API client for testing API endpoints."""
    return APIClient()


@pytest.fixture
def django_client():
    """Provides Django test client."""
    return Client()


@pytest.fixture
def sample_address():
    """Creates a sample address for testing."""
    return AddressFactory()


@pytest.fixture
def sample_user(sample_address):
    """Creates a sample user with address for testing."""
    return AppUserFactory(address=sample_address)


@pytest.fixture
def sample_user_with_relationship(sample_user):
    """Creates a sample user with customer relationship."""
    relationship = CustomerRelationshipFactory(appuser=sample_user)
    return relationship


@pytest.fixture
def multiple_users():
    """Creates multiple users for list testing."""
    users = []
    for i in range(5):
        user = AppUserFactory()
        CustomerRelationshipFactory(appuser=user)
        users.append(user)
    return users


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    cache.clear()
    yield
    cache.clear()