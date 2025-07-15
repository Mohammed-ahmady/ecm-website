"""
Tests for parts views.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
import json
from parts.models import Part, Category, TruckModel, CartItem, Order
from .test_utils import BaseTestCase, create_test_part, create_test_category


class PartListViewTest(BaseTestCase):
    """Test cases for PartListView"""
    
    def test_part_list_view_get(self):
        """Test GET request to part list view"""
        response = self.client.get(reverse('parts:part_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.part.name)
        self.assertIn('parts', response.context)
    
    def test_part_list_search(self):
        """Test search functionality in part list"""
        response = self.client.get(reverse('parts:part_list'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.part.name)
    
    def test_part_list_category_filter(self):
        """Test category filtering in part list"""
        response = self.client.get(reverse('parts:part_list'), {
            'category': self.category.slug
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.part.name)
    
    def test_part_list_truck_model_filter(self):
        """Test truck model filtering in part list"""
        response = self.client.get(reverse('parts:part_list'), {
            'truck_model': self.truck_model.slug
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.part.name)


class PartDetailViewTest(BaseTestCase):
    """Test cases for PartDetailView"""
    
    def test_part_detail_view(self):
        """Test part detail view with valid part"""
        response = self.client.get(
            reverse('parts:part_detail', kwargs={'slug': self.part.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.part.name)
        self.assertEqual(response.context['part'], self.part)
    
    def test_inactive_part_detail_404(self):
        """Test that inactive parts return 404"""
        inactive_part = create_test_part("Inactive Part", "IP001", is_active=False)
        response = self.client.get(
            reverse('parts:part_detail', kwargs={'slug': inactive_part.slug})
        )
        self.assertEqual(response.status_code, 404)


class CartViewTest(BaseTestCase):
    """Test cases for cart-related views"""
    
    def setUp(self):
        super().setUp()
        self.client = Client()
        # Create a session
        session = self.client.session
        session.save()
    
    def test_add_to_cart_post(self):
        """Test adding item to cart via POST"""
        response = self.client.post(
            reverse('parts:add_to_cart', kwargs={'part_id': self.part.id}),
            {'quantity': 2}
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check if cart item was created
        cart_items = CartItem.objects.filter(part=self.part)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 2)
    
    def test_add_to_cart_ajax(self):
        """Test adding item to cart via AJAX"""
        response = self.client.post(
            reverse('parts:add_to_cart', kwargs={'part_id': self.part.id}),
            {'quantity': 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('message', data)
    
    def test_cart_detail_view(self):
        """Test cart detail view"""
        # Add item to cart first
        CartItem.objects.create(
            session_key=self.client.session.session_key,
            part=self.part,
            quantity=2
        )
        
        response = self.client.get(reverse('parts:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('cart_items', response.context)
        self.assertIn('total_price', response.context)
    
    def test_remove_from_cart(self):
        """Test removing item from cart"""
        # Add item to cart first
        CartItem.objects.create(
            session_key=self.client.session.session_key,
            part=self.part,
            quantity=1
        )
        
        response = self.client.post(
            reverse('parts:remove_from_cart', kwargs={'part_id': self.part.id})
        )
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check if cart item was removed
        cart_items = CartItem.objects.filter(
            session_key=self.client.session.session_key,
            part=self.part
        )
        self.assertEqual(cart_items.count(), 0)


class HomeViewTest(BaseTestCase):
    """Test cases for home view"""
    
    def test_home_view(self):
        """Test home page view"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('truck_models', response.context)
        self.assertContains(response, self.truck_model.name)


class InquiryViewTest(BaseTestCase):
    """Test cases for inquiry view"""
    
    def test_inquiry_view_get(self):
        """Test GET request to inquiry view"""
        response = self.client.get(reverse('inquiry'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_inquiry_view_post_valid(self):
        """Test POST request with valid inquiry data"""
        data = {
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'customer_phone': '+1234567890',
            'truck_model': self.truck_model.id,
            'part_needed': 'Brake pads',
            'message': 'I need brake pads for my truck'
        }
        response = self.client.post(reverse('inquiry'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success


class CheckoutViewTest(BaseTestCase):
    """Test cases for checkout view"""
    
    def setUp(self):
        super().setUp()
        # Add item to cart for checkout tests
        CartItem.objects.create(
            session_key=self.client.session.session_key,
            part=self.part,
            quantity=1
        )
    
    def test_checkout_view_get(self):
        """Test GET request to checkout view"""
        response = self.client.get(reverse('parts:checkout_page'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('cart_items', response.context)
        self.assertIn('total_price', response.context)
    
    def test_checkout_empty_cart_redirect(self):
        """Test checkout with empty cart redirects"""
        # Clear cart
        CartItem.objects.filter(
            session_key=self.client.session.session_key
        ).delete()
        
        response = self.client.get(reverse('parts:checkout_page'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_checkout_post_valid(self):
        """Test POST request with valid checkout data"""
        data = {
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'customer_phone': '+1234567890',
            'shipping_address': '123 Test St',
            'city': 'Test City',
            'country': 'Test Country'
        }
        response = self.client.post(reverse('parts:checkout_page'), data)
        self.assertEqual(response.status_code, 200)  # Success page
        
        # Check if order was created
        orders = Order.objects.filter(customer_email='john@example.com')
        self.assertEqual(orders.count(), 1)
