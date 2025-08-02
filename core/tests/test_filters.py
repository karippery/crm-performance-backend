import pytest
from datetime import date, datetime
from django.db.models import Q
from core.filters import build_appuser_filters
from core.tests.conftest import AppUserFactory, CustomerRelationshipFactory


class TestBuildAppUserFilters:
    """Test cases for build_appuser_filters function."""

    def test_empty_params(self):
        """Test with empty parameters."""
        filters = build_appuser_filters({})
        assert filters == Q()

    def test_first_name_filter(self):
        """Test first name filtering."""
        params = {'first_name': 'John'}
        filters = build_appuser_filters(params)
        
        expected = Q(first_name__icontains='John')
        assert filters == expected

    def test_last_name_filter(self):
        """Test last name filtering."""
        params = {'last_name': 'Doe'}
        filters = build_appuser_filters(params)
        
        expected = Q(last_name__icontains='Doe')
        assert filters == expected

    def test_gender_filter(self):
        """Test gender filtering."""
        params = {'gender': 'Male'}
        filters = build_appuser_filters(params)
        
        expected = Q(gender='Male')
        assert filters == expected

    def test_customer_id_filter(self):
        """Test customer ID filtering."""
        params = {'customer_id': 'CUST123456'}
        filters = build_appuser_filters(params)
        
        expected = Q(customer_id='CUST123456')
        assert filters == expected

    def test_phone_number_filter(self):
        """Test phone number filtering."""
        params = {'phone_number': '555-1234'}
        filters = build_appuser_filters(params)
        
        expected = Q(phone_number__icontains='555-1234')
        assert filters == expected

    def test_birthday_filter_string(self):
        """Test birthday filtering with string date."""
        params = {'birthday': '1990-05-15'}
        filters = build_appuser_filters(params)
        
        expected = Q(birthday=date(1990, 5, 15))
        assert filters == expected

    def test_birthday_filter_date_object(self):
        """Test birthday filtering with date object."""
        birthday = date(1990, 5, 15)
        params = {'birthday': birthday}
        filters = build_appuser_filters(params)
        
        expected = Q(birthday=birthday)
        assert filters == expected

    def test_invalid_birthday_filter(self):
        """Test birthday filtering with invalid date."""
        params = {'birthday': 'invalid-date'}
        filters = build_appuser_filters(params)
        
        # Invalid date should be ignored
        assert filters == Q()

    def test_address_filters(self):
        """Test address-related filters."""
        params = {
            'city': 'Berlin',
            'street': 'Main',
            'country': 'Germany'
        }
        filters = build_appuser_filters(params)
        
        expected = (
            Q(address__city__icontains='Berlin') &
            Q(address__street__icontains='Main') &
            Q(address__country__icontains='Germany')
        )
        assert filters == expected

    def test_points_filters(self):
        """Test points-related filters."""
        params = {
            'points_min': '100',
            'points_max': '1000'
        }
        filters = build_appuser_filters(params)
        
        expected = (
            Q(relationships__points__gte=100) &
            Q(relationships__points__lte=1000)
        )
        assert filters == expected

    def test_invalid_points_filters(self):
        """Test points filters with invalid values."""
        params = {
            'points_min': 'invalid',
            'points_max': 'also-invalid'
        }
        filters = build_appuser_filters(params)
        
        # Invalid values should be ignored
        assert filters == Q()

    def test_last_activity_filter(self):
        """Test last activity filtering."""
        params = {'last_activity_after': '2023-01-01'}
        filters = build_appuser_filters(params)
        
        expected = Q(relationships__last_activity__gte=datetime(2023, 1, 1))
        assert filters == expected

    def test_combined_filters(self):
        """Test combining multiple filters."""
        params = {
            'first_name': 'John',
            'gender': 'Male',
            'city': 'Berlin',
            'points_min': '100'
        }
        filters = build_appuser_filters(params)
        
        expected = (
            Q(first_name__icontains='John') &
            Q(gender='Male') &
            Q(address__city__icontains='Berlin') &
            Q(relationships__points__gte=100)
        )
        assert filters == expected

    def test_whitespace_handling(self):
        """Test that whitespace is properly stripped."""
        params = {
            'first_name': '  John  ',
            'last_name': '\tDoe\n'
        }
        filters = build_appuser_filters(params)
        
        expected = (
            Q(first_name__icontains='John') &
            Q(last_name__icontains='Doe')
        )
        assert filters == expected