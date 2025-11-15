"""
Tests for the Equipment application.
Includes unit tests for models, views, serializers, and utilities.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import pandas as pd
import io

from .models import Dataset, EquipmentData
from .utils import validate_csv_structure, parse_csv_file, analyze_equipment_data


class DatasetModelTests(TestCase):
    """Tests for the Dataset model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
    def test_dataset_creation(self):
        """Test creating a dataset."""
        dataset = Dataset.objects.create(
            user=self.user,
            filename='test.csv',
            total_count=10,
            avg_flowrate=100.0,
            avg_pressure=5.0,
            avg_temperature=110.0
        )
        self.assertEqual(dataset.filename, 'test.csv')
        self.assertEqual(dataset.total_count, 10)
        
    def test_get_summary(self):
        """Test the get_summary method."""
        dataset = Dataset.objects.create(
            user=self.user,
            filename='test.csv',
            total_count=10
        )
        summary = dataset.get_summary()
        self.assertIn('filename', summary)
        self.assertIn('total_count', summary)


class CSVUploadAPITests(APITestCase):
    """Tests for CSV upload API endpoint."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def create_csv_file(self, content):
        """Helper to create a CSV file."""
        return SimpleUploadedFile(
            "test.csv",
            content.encode('utf-8'),
            content_type="text/csv"
        )
    
    def test_upload_valid_csv(self):
        """Test uploading a valid CSV file."""
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
Compressor-1,Compressor,95,8.4,95"""
        
        csv_file = self.create_csv_file(csv_content)
        response = self.client.post('/api/datasets/upload_csv/', {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
    def test_upload_invalid_csv(self):
        """Test uploading an invalid CSV file."""
        csv_content = """Invalid,Headers
1,2"""
        
        csv_file = self.create_csv_file(csv_content)
        response = self.client.post('/api/datasets/upload_csv/', {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthenticationAPITests(APITestCase):
    """Tests for authentication endpoints."""
    
    def test_user_registration(self):
        """Test user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        
    def test_user_login(self):
        """Test user login."""
        User.objects.create_user(username='testuser', password='testpass123')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_invalid_login(self):
        """Test login with invalid credentials."""
        User.objects.create_user(username='testuser', password='testpass123')
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DatasetHistoryTests(APITestCase):
    """Tests for dataset history functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_history_returns_last_five(self):
        """Test that history returns only last 5 datasets."""
        # Create 7 datasets
        for i in range(7):
            Dataset.objects.create(
                user=self.user,
                filename=f'test{i}.csv',
                total_count=10
            )
        
        response = self.client.get('/api/datasets/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return only 5 datasets
        self.assertLessEqual(len(response.data), 5)
    
    def test_delete_dataset(self):
        """Test deleting a dataset."""
        dataset = Dataset.objects.create(
            user=self.user,
            filename='test.csv',
            total_count=10
        )
        response = self.client.delete(f'/api/datasets/{dataset.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Dataset.objects.filter(id=dataset.id).exists())


class UtilityFunctionTests(TestCase):
    """Tests for utility functions."""
    
    def test_validate_csv_structure_valid(self):
        """Test CSV validation with valid structure."""
        df = pd.DataFrame({
            'Equipment Name': ['Pump-1'],
            'Type': ['Pump'],
            'Flowrate': [120],
            'Pressure': [5.2],
            'Temperature': [110]
        })
        is_valid, error = validate_csv_structure(df)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_csv_structure_invalid(self):
        """Test CSV validation with invalid structure."""
        df = pd.DataFrame({
            'Invalid': ['data'],
            'Columns': ['here']
        })
        is_valid, error = validate_csv_structure(df)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_analyze_equipment_data(self):
        """Test equipment data analysis."""
        df = pd.DataFrame({
            'Equipment Name': ['Pump-1', 'Compressor-1'],
            'Type': ['Pump', 'Compressor'],
            'Flowrate': [120, 95],
            'Pressure': [5.2, 8.4],
            'Temperature': [110, 95]
        })
        
        analysis = analyze_equipment_data(df)
        self.assertIn('total_count', analysis)
        self.assertIn('equipment_distribution', analysis)
        self.assertIn('avg_parameters', analysis)
        self.assertEqual(analysis['total_count'], 2)
