from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()

class UserProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse('user_profile')

    def test_get_profile(self):
        """Test retrieving user profile"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('qabiil', response.data)
        self.assertIn('laan', response.data)
        self.assertIn('laan_choices', response.data)

    def test_update_profile_valid_data(self):
        """Test updating profile with valid data"""
        data = {
            'qabiil': 'Daarood',
            'laan': 'Harti'
        }
        response = self.client.put(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['qabiil'], 'Daarood')
        self.assertEqual(response.data['laan'], 'Harti')

    def test_update_profile_invalid_qabiil(self):
        """Test updating profile with invalid qabiil"""
        data = {
            'qabiil': 'InvalidQabiil',
            'laan': 'Harti'
        }
        response = self.client.put(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_invalid_laan(self):
        """Test updating profile with invalid laan for qabiil"""
        data = {
            'qabiil': 'Daarood',
            'laan': 'InvalidLaan'
        }
        response = self.client.put(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_profile_partial_data(self):
        """Test updating profile with partial data"""
        data = {
            'qabiil': 'Daarood'
        }
        response = self.client.put(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['qabiil'], 'Daarood')
        self.assertIsNone(response.data['laan'])

    def test_laan_choices_updates_with_qabiil(self):
        """Test that laan choices update when qabiil changes"""
        # First set qabiil to Daarood
        data = {'qabiil': 'Daarood'}
        response = self.client.put(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Harti', response.data['laan_choices'])

        # Then change to Hawiye
        data = {'qabiil': 'Hawiye'}
        response = self.client.put(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Abgaal', response.data['laan_choices'])
        self.assertNotIn('Harti', response.data['laan_choices']) 