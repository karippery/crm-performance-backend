import pytest
from datetime import date, timedelta
from django.utils import timezone
from core.models import AppUser, CustomerRelationship
from core.tests.conftest import AppUserFactory, CustomerRelationshipFactory


@pytest.mark.django_db
class TestIntegration:
    """Integration tests combining multiple components."""

    def test_complete_user_creation_workflow(self):
        """Test complete workflow of creating user with relationships."""
        # Create user
        user = AppUserFactory(
            first_name='John',
            last_name='Doe',
            gender='Male',
            birthday=date(1990, 5, 15)
        )
        
        # Add relationships
        relationship1 = CustomerRelationshipFactory(
            appuser=user,
            points=100,
            created=timezone.now() - timedelta(days=30)
        )
        relationship2 = CustomerRelationshipFactory(
            appuser=user,
            points=200,
            created=timezone.now() - timedelta(days=15)
        )
        
        # Verify user exists and has correct data
        assert AppUser.objects.filter(customer_id=user.customer_id).exists()
        
        # Verify relationships
        user_relationships = CustomerRelationship.objects.filter(appuser=user)
        assert user_relationships.count() == 2
        
        # Verify ordering (should be ordered by -created)
        ordered_relationships = list(user_relationships.order_by('-created'))
        assert ordered_relationships[0] == relationship2
        assert ordered_relationships[1] == relationship1

    def test_user_deletion_cascade(self):
        """Test that deleting user cascades to relationships."""
        user = AppUserFactory()
        relationship = CustomerRelationshipFactory(appuser=user)
        
        relationship_id = relationship.id
        user_id = user.id
        
        # Delete user
        user.delete()
        
        # Verify user is deleted
        assert not AppUser.objects.filter(id=user_id).exists()
        
        # Verify relationship is also deleted (cascade)
        assert not CustomerRelationship.objects.filter(id=relationship_id).exists()

    def test_address_relationship_integrity(self):
        """Test address and user relationship integrity."""
        user = AppUserFactory()
        address = user.address
        
        # Verify relationship
        assert address.users.filter(id=user.id).exists()
        
        # Delete address should delete user (cascade)
        address_id = address.id
        user_id = user.id
        
        address.delete()
        
        assert not AppUser.objects.filter(id=user_id).exists()