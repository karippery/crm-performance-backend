# management/commands/populate_data.py
import random
import string
from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from core.models import Address, AppUser, CustomerRelationship

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=3000000,
            help='Number of users to create (default: 3,000,000)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10000,
            help='Batch size for bulk operations (default: 10,000)'
        )

    def handle(self, *args, **options):
        fake = Faker(['en_US', 'de_DE', 'fr_FR'])
        num_users = options['users']
        batch_size = options['batch_size']
        
        self.stdout.write(f"Creating {num_users:,} users in batches of {batch_size:,}")
        
        # First, create addresses in bulk
        self.stdout.write("Creating addresses...")
        addresses = self.create_addresses(fake, num_users, batch_size)
        
        # Then create users and relationships
        self.stdout.write("Creating users and relationships...")
        self.create_users_and_relationships(fake, addresses, batch_size)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {num_users:,} users with addresses and relationships')
        )

    def create_addresses(self, fake, num_addresses, batch_size):
        """Create addresses in bulk and return list of created objects"""
        addresses = []
        total_created = 0
        
        for batch_start in range(0, num_addresses, batch_size):
            batch_addresses = []
            batch_end = min(batch_start + batch_size, num_addresses)
            
            for _ in range(batch_end - batch_start):
                address = Address(
                    street=fake.street_name(),
                    street_number=str(random.randint(1, 999)),
                    city_code=fake.postcode(),
                    city=fake.city(),
                    country=fake.country()
                )
                batch_addresses.append(address)
            
            # Bulk create and get back the objects with IDs
            created_addresses = Address.objects.bulk_create(batch_addresses)
            addresses.extend(created_addresses)
            total_created += len(created_addresses)
            
            if batch_start % (batch_size * 10) == 0:
                self.stdout.write(f"Created {total_created:,} addresses...")
        
        return addresses

    def create_users_and_relationships(self, fake, addresses, batch_size):
        """Create users and relationships in bulk"""
        total_created = 0
        
        for batch_start in range(0, len(addresses), batch_size):
            batch_end = min(batch_start + batch_size, len(addresses))
            batch_users = []
            batch_relationships = []
            
            for i in range(batch_start, batch_end):
                address = addresses[i]
                
                # Generate user
                user = AppUser(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    gender=random.choice(['Male', 'Female', 'Other', 'Prefer not to say']),
                    customer_id=self.generate_customer_id(),
                    phone_number=fake.phone_number() if random.random() > 0.2 else None,
                    address=address,
                    birthday=fake.date_of_birth(minimum_age=18, maximum_age=80) if random.random() > 0.1 else None,
                    created=fake.date_time_between(start_date='-2y', end_date='now'),
                )
                batch_users.append(user)
            
            # Bulk create users
            with transaction.atomic():
                created_users = AppUser.objects.bulk_create(batch_users)
                
                # Create relationships for the created users
                for user in created_users:
                    relationship = CustomerRelationship(
                        appuser=user,
                        relationship_type=random.choice(['BASIC', 'PREMIUM', 'VIP']),
                        points=random.randint(0, 10000),
                        created=user.created + timedelta(days=random.randint(0, 30)),
                        last_activity=fake.date_time_between(
                            start_date=user.created, 
                            end_date='now'
                        ) if random.random() > 0.3 else None
                    )
                    batch_relationships.append(relationship)
                
                # Bulk create relationships
                CustomerRelationship.objects.bulk_create(batch_relationships)
            
            total_created += len(created_users)
            
            if batch_start % (batch_size * 10) == 0:
                self.stdout.write(f"Created {total_created:,} users and relationships...")

    def generate_customer_id(self):
        """Generate unique customer ID"""
        prefix = 'CRM'
        timestamp = int(datetime.now().timestamp() * 1000000)  # microseconds
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix}{timestamp}{random_suffix}"