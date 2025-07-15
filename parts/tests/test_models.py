"""
Tests for parts models.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from parts.models import Category, TruckModel, Engine, Part, CartItem, Order, OrderItem
from .test_utils import BaseTestCase, create_test_category, create_test_truck_model, create_test_part


class CategoryModelTest(BaseTestCase):
    """Test cases for Category model"""
    
    def test_category_creation(self):
        """Test creating a category"""
        category = create_test_category("Engine Parts")
        self.assertEqual(str(category), "Engine Parts")
        self.assertEqual(category.slug, "engine-parts")
    
    def test_category_unique_name(self):
        """Test that category names must be unique"""
        create_test_category("Unique Category")
        with self.assertRaises(IntegrityError):
            create_test_category("Unique Category")
    
    def test_category_slug_generation(self):
        """Test automatic slug generation"""
        category = create_test_category("Test Category With Spaces")
        self.assertEqual(category.slug, "test-category-with-spaces")


class TruckModelTest(BaseTestCase):
    """Test cases for TruckModel model"""
    
    def test_truck_model_creation(self):
        """Test creating a truck model"""
        truck = create_test_truck_model("Magirus 290M")
        self.assertEqual(str(truck), "Magirus Magirus 290M")
        self.assertEqual(truck.slug, "magirus-290m")
    
    def test_truck_model_with_engines(self):
        """Test truck model with associated engines"""
        truck = create_test_truck_model("Test Truck")
        engine = Engine.objects.create(
            name="Test Engine",
            power_output="250 HP",
            fuel_type="Diesel"
        )
        engine.truck_models.add(truck)
        
        self.assertIn(engine, truck.engines.all())
        self.assertIn(truck, engine.truck_models.all())


class PartModelTest(BaseTestCase):
    """Test cases for Part model"""
    
    def test_part_creation(self):
        """Test creating a part"""
        part = create_test_part("Brake Disc", "BD001")
        self.assertIn("Brake Disc", str(part))
        self.assertEqual(part.part_number, "BD001")
        self.assertTrue(part.is_active)
    
    def test_part_with_truck_models(self):
        """Test part associated with truck models"""
        part = create_test_part("Test Part")
        truck = create_test_truck_model("Test Truck")
        part.truck_models.add(truck)
        
        self.assertIn(truck, part.truck_models.all())
    
    def test_part_price_validation(self):
        """Test part price validation"""
        part = create_test_part("Expensive Part", price=1000.00)
        self.assertEqual(part.price, 1000.00)
    
    def test_part_stock(self):
        """Test part stock quantity"""
        part = create_test_part("Stocked Part", stock=50)
        self.assertEqual(part.stock, 50)


class CartItemModelTest(BaseTestCase):
    """Test cases for CartItem model"""
    
    def test_cart_item_creation(self):
        """Test creating a cart item"""
        cart_item = CartItem.objects.create(
            session_key="test_session",
            part=self.part,
            quantity=2
        )
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.part, self.part)
    
    def test_cart_item_total_price(self):
        """Test cart item total price calculation"""
        cart_item = CartItem.objects.create(
            session_key="test_session",
            part=self.part,
            quantity=3
        )
        expected_total = self.part.price * 3
        self.assertEqual(cart_item.total_price, expected_total)


class OrderModelTest(BaseTestCase):
    """Test cases for Order model"""
    
    def test_order_creation(self):
        """Test creating an order"""
        order = Order.objects.create(
            customer_name="John Doe",
            customer_email="john@example.com",
            customer_phone="+1234567890",
            shipping_address="123 Test St",
            city="Test City",
            country="Test Country",
            total_amount=199.98
        )
        self.assertEqual(order.customer_name, "John Doe")
        self.assertTrue(order.order_id)  # Should have generated ID
    
    def test_order_with_items(self):
        """Test order with order items"""
        order = Order.objects.create(
            customer_name="Jane Doe",
            customer_email="jane@example.com",
            customer_phone="+1234567890",
            shipping_address="456 Test Ave",
            city="Test City",
            country="Test Country",
            total_amount=99.99
        )
        
        order_item = OrderItem.objects.create(
            order=order,
            part=self.part,
            quantity=1,
            price=self.part.price
        )
        
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order_item.total_price, self.part.price)
