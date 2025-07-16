"""
Test utilities and fixtures for parts app.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from parts.models import Category, TruckModel, Engine, Part, CartItem, Order, OrderItem


class BaseTestCase(TestCase):
    """Base test case with common setup for parts app tests"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name="Test Category",
            description="A test category for testing"
        )
        
        self.truck_model = TruckModel.objects.create(
            name="Test Truck Model",
            manufacturer="Magirus",
            year_range="2020-2023",
            description="A test truck model"
        )
        
        self.engine = Engine.objects.create(
            name="Test Engine",
            power_output="300 HP",
            fuel_type="Diesel",
            emissions_standard="Euro 6"
        )
        self.engine.truck_models.add(self.truck_model)
        
        self.part = Part.objects.create(
            name="Test Part",
            part_number="TP001",
            category=self.category,
            price=99.99,
            description="A test part for testing",
            is_active=True,
            stock=10
        )
        self.part.truck_models.add(self.truck_model)
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )


def create_test_part(name="Test Part", part_number=None, category=None, **kwargs):
    """Helper function to create a test part"""
    if category is None:
        category = Category.objects.create(name="Default Category")
    
    # Generate unique part number if not provided
    if part_number is None:
        import uuid
        part_number = f"TP{uuid.uuid4().hex[:6].upper()}"
    
    defaults = {
        'price': 99.99,
        'description': f"Test description for {name}",
        'is_active': True,
        'stock': 10
    }
    defaults.update(kwargs)
    
    return Part.objects.create(
        name=name,
        part_number=part_number,
        category=category,
        **defaults
    )


def create_test_category(name="Test Category", **kwargs):
    """Helper function to create a test category"""
    defaults = {
        'description': f"Test description for {name}"
    }
    defaults.update(kwargs)
    
    return Category.objects.create(name=name, **defaults)


def create_test_truck_model(name="Test Truck", **kwargs):
    """Helper function to create a test truck model"""
    defaults = {
        'manufacturer': 'Magirus',
        'year_range': '2020-2023',
        'description': f"Test description for {name}"
    }
    defaults.update(kwargs)
    
    return TruckModel.objects.create(name=name, **defaults)
