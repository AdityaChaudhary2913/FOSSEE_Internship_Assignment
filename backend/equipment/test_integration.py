"""
Integration tests for the complete workflow.
Tests the full user journey from registration to PDF generation.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import io

from .models import Dataset, EquipmentData


class CompleteWorkflowTests(APITestCase):
    """Test the complete user workflow."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        
    def create_csv_file(self):
        """Create a valid CSV file for testing."""
        csv_content = """Equipment_ID,Equipment_Type,Temperature,Pressure,Flow_Rate,Efficiency
EQ001,Pump,75.5,2.3,150.0,92.5
EQ002,Compressor,95.0,8.5,200.0,88.0
EQ003,Valve,65.0,1.5,100.0,95.0
EQ004,HeatExchanger,150.0,3.0,175.0,90.0
EQ005,Reactor,200.0,10.0,50.0,85.0"""
        
        return SimpleUploadedFile(
            "equipment_data.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
    
    def test_complete_user_journey(self):
        """Test the complete user journey from registration to PDF generation."""
        
        # Step 1: User Registration
        register_data = {
            'username': 'journeyuser',
            'email': 'journey@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
        register_response = self.client.post('/api/auth/register/', register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', register_response.data)
        
        token = register_response.data['token']
        
        # Step 2: Authenticate for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # Step 3: Upload CSV file
        csv_file = self.create_csv_file()
        upload_response = self.client.post(
            '/api/datasets/upload_csv/',
            {'file': csv_file, 'name': 'Test Equipment Data'},
            format='multipart'
        )
        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(upload_response.data['success'])
        
        dataset_id = upload_response.data['dataset_id']
        
        # Step 4: Verify dataset was created
        self.assertTrue(Dataset.objects.filter(id=dataset_id).exists())
        dataset = Dataset.objects.get(id=dataset_id)
        self.assertEqual(dataset.user.username, 'journeyuser')
        
        # Step 5: Get dataset summary
        summary_response = self.client.get(f'/api/datasets/{dataset_id}/summary/')
        self.assertEqual(summary_response.status_code, status.HTTP_200_OK)
        self.assertIn('total_count', summary_response.data)
        self.assertEqual(summary_response.data['total_count'], 5)
        
        # Step 6: Check history
        history_response = self.client.get('/api/datasets/history/')
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_response.data), 1)
        
        # Step 7: Generate PDF
        pdf_response = self.client.get(f'/api/datasets/{dataset_id}/generate_pdf/')
        self.assertEqual(pdf_response.status_code, status.HTTP_200_OK)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
        
        # Step 8: Delete dataset
        delete_response = self.client.delete(f'/api/datasets/{dataset_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Step 9: Verify dataset is deleted
        self.assertFalse(Dataset.objects.filter(id=dataset_id).exists())
        
        # Step 10: Logout
        logout_response = self.client.post('/api/auth/logout/')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)


class MultipleUploadsTests(APITestCase):
    """Test multiple CSV uploads and history management."""
    
    def setUp(self):
        """Set up authenticated user."""
        self.user = User.objects.create_user(
            username='multiuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def create_csv_file(self, filename):
        """Create a CSV file with given filename."""
        csv_content = """Equipment_ID,Equipment_Type,Temperature,Pressure,Flow_Rate,Efficiency
EQ001,Pump,75.5,2.3,150.0,92.5"""
        
        return SimpleUploadedFile(
            filename,
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
    
    def test_upload_multiple_files(self):
        """Test uploading multiple CSV files."""
        
        # Upload 3 files
        for i in range(3):
            csv_file = self.create_csv_file(f'test_{i}.csv')
            response = self.client.post(
                '/api/datasets/upload_csv/',
                {'file': csv_file, 'name': f'Dataset {i}'},
                format='multipart'
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check history
        history_response = self.client.get('/api/datasets/history/')
        self.assertEqual(len(history_response.data), 3)
    
    def test_history_limit_to_five(self):
        """Test that history only keeps last 5 datasets."""
        
        # Upload 7 files
        dataset_ids = []
        for i in range(7):
            csv_file = self.create_csv_file(f'test_{i}.csv')
            response = self.client.post(
                '/api/datasets/upload_csv/',
                {'file': csv_file, 'name': f'Dataset {i}'},
                format='multipart'
            )
            dataset_ids.append(response.data['dataset_id'])
        
        # Check that only 5 datasets exist
        total_datasets = Dataset.objects.filter(user=self.user).count()
        self.assertLessEqual(total_datasets, 5)
        
        # Check history returns max 5
        history_response = self.client.get('/api/datasets/history/')
        self.assertLessEqual(len(history_response.data), 5)


class ErrorHandlingTests(APITestCase):
    """Test error handling scenarios."""
    
    def setUp(self):
        """Set up authenticated user."""
        self.user = User.objects.create_user(
            username='erroruser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_upload_invalid_file_type(self):
        """Test uploading a non-CSV file."""
        txt_file = SimpleUploadedFile(
            "test.txt",
            b"This is not a CSV file",
            content_type="text/plain"
        )
        
        response = self.client.post(
            '/api/datasets/upload_csv/',
            {'file': txt_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_upload_missing_columns(self):
        """Test uploading CSV with missing required columns."""
        csv_content = """Column1,Column2
Value1,Value2"""
        
        csv_file = SimpleUploadedFile(
            "invalid.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(
            '/api/datasets/upload_csv/',
            {'file': csv_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoints without authentication."""
        # Create unauthenticated client
        unauth_client = APIClient()
        
        # Try to access history
        response = unauth_client.get('/api/datasets/history/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try to upload
        csv_file = SimpleUploadedFile(
            "test.csv",
            b"Equipment_ID,Equipment_Type,Temperature,Pressure,Flow_Rate,Efficiency\n",
            content_type="text/csv"
        )
        response = unauth_client.post(
            '/api/datasets/upload_csv/',
            {'file': csv_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_access_other_user_dataset(self):
        """Test that users can't access other users' datasets."""
        # Create another user's dataset
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        other_dataset = Dataset.objects.create(
            user=other_user,
            filename='other.csv',
            total_count=10
        )
        
        # Try to access it with current user
        response = self.client.get(f'/api/datasets/{other_dataset.id}/summary/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DataValidationTests(APITestCase):
    """Test data validation logic."""
    
    def setUp(self):
        """Set up authenticated user."""
        self.user = User.objects.create_user(
            username='validuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_csv_with_empty_values(self):
        """Test CSV with empty values."""
        csv_content = """Equipment_ID,Equipment_Type,Temperature,Pressure,Flow_Rate,Efficiency
EQ001,Pump,75.5,2.3,150.0,92.5
EQ002,Compressor,,,200.0,88.0"""
        
        csv_file = SimpleUploadedFile(
            "partial.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(
            '/api/datasets/upload_csv/',
            {'file': csv_file},
            format='multipart'
        )
        # Should handle empty values gracefully
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_large_csv_file(self):
        """Test uploading a large CSV file."""
        # Create CSV with many rows
        rows = ["Equipment_ID,Equipment_Type,Temperature,Pressure,Flow_Rate,Efficiency"]
        for i in range(1000):
            rows.append(f"EQ{i:04d},Pump,75.5,2.3,150.0,92.5")
        
        csv_content = "\n".join(rows)
        csv_file = SimpleUploadedFile(
            "large.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(
            '/api/datasets/upload_csv/',
            {'file': csv_file},
            format='multipart'
        )
        # Should handle large files
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
