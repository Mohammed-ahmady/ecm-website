"""
Tests for parts utilities.
"""
from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.db.models import QuerySet
from parts.utils import ModernCart, get_cart_response_data, is_ajax_request, get_search_queryset
from parts.models import Part, CartItem
from .test_utils import BaseTestCase, create_test_part


class ModernCartTest(BaseTestCase):
    """Test cases for ModernCart utility class"""
    
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.session = SessionStore()
        self.request.session.create()
        self.cart = ModernCart(self.request)
    
    def test_cart_initialization(self):
        """Test cart initialization with session"""
        self.assertIsNotNone(self.cart.session_key)
        self.assertEqual(self.cart.session, self.request.session)
    
    def test_add_new_item(self):
        """Test adding a new item to cart"""
        cart_item = self.cart.add(self.part, 2)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.part, self.part)
    
    def test_add_existing_item(self):
        """Test adding to existing item in cart"""
        # Add initial item
        self.cart.add(self.part, 1)
        # Add more of the same item
        cart_item = self.cart.add(self.part, 2)
        self.assertEqual(cart_item.quantity, 3)
    
    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        self.cart.add(self.part, 1)
        self.cart.update(self.part, 5)
        
        cart_item = CartItem.objects.get(
            session_key=self.cart.session_key,
            part=self.part
        )
        self.assertEqual(cart_item.quantity, 5)
    
    def test_remove_cart_item(self):
        """Test removing item from cart"""
        self.cart.add(self.part, 1)
        self.cart.remove(self.part)
        
        cart_items = CartItem.objects.filter(
            session_key=self.cart.session_key,
            part=self.part
        )
        self.assertEqual(cart_items.count(), 0)
    
    def test_get_total_price(self):
        """Test calculating total cart price"""
        self.cart.add(self.part, 2)
        total_price = self.cart.get_total_price()
        expected_total = self.part.price * 2
        
        self.assertEqual(float(total_price), float(expected_total))
    
    def test_clear_cart(self):
        """Test clearing all items from cart"""
        self.cart.add(self.part, 2)
        self.cart.clear()
        
        items = self.cart.get_items()
        self.assertEqual(items.count(), 0)


class UtilityFunctionsTest(TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get_cart_response_data(self):
        """Test get_cart_response_data function"""
        # Create a mock cart object
        class MockCart:
            def get_total_items(self):
                return 5
            def get_total_price(self):
                return 199.95
        
        cart = MockCart()
        response_data = get_cart_response_data(cart)
        
        self.assertEqual(response_data['cart_total_items'], 5)
        self.assertEqual(response_data['cart_total_price'], 199.95)
    
    def test_is_ajax_request_true(self):
        """Test is_ajax_request returns True for AJAX requests"""
        request = self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(is_ajax_request(request))
    
    def test_is_ajax_request_false(self):
        """Test is_ajax_request returns False for non-AJAX requests"""
        request = self.factory.get('/')
        self.assertFalse(is_ajax_request(request))


class SearchQuerysetTest(BaseTestCase):
    """Test cases for search queryset utility"""
    
    def setUp(self):
        super().setUp()
        # Create additional test data
        self.part2 = create_test_part(
            "Brake Disc",
            "BD001",
            category=self.category,
            description="High quality brake disc"
        )
        self.part2.truck_models.add(self.truck_model)
    
    def test_search_by_name(self):
        """Test searching by part name"""
        queryset = Part.objects.all()
        result = get_search_queryset(queryset, {'q': 'Brake'})
        
        self.assertIn(self.part2, result)
        self.assertNotIn(self.part, result)
    
    def test_filter_by_category(self):
        """Test filtering by category"""
        queryset = Part.objects.all()
        result = get_search_queryset(queryset, {'category': self.category.slug})
        
        self.assertIn(self.part, result)
        self.assertIn(self.part2, result)
    
    def test_empty_query_params(self):
        """Test with empty query parameters"""
        queryset = Part.objects.all()
        result = get_search_queryset(queryset, {})
        
        # Should return original queryset
        self.assertEqual(list(result), list(queryset))
