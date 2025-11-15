"""
API Views for the Equipment application.
Implements REST endpoints for CSV upload, data analysis, and dataset management.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from django.conf import settings
from django.http import FileResponse, HttpResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os

from .models import Dataset, EquipmentData
from .serializers import (
    DatasetSerializer, DatasetSummarySerializer, EquipmentDataSerializer,
    CSVUploadSerializer, UserSerializer, UserRegistrationSerializer
)
from .utils import (
    parse_csv_file, analyze_equipment_data, generate_pdf_report,
    convert_dataframe_to_list
)


class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing datasets.
    Provides CRUD operations and custom actions for CSV upload and PDF generation.
    """
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return datasets for the current user only."""
        return Dataset.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use summary serializer for list view."""
        if self.action == 'list':
            return DatasetSummarySerializer
        return DatasetSerializer
    
    @swagger_auto_schema(
        method='post',
        request_body=CSVUploadSerializer,
        responses={
            201: DatasetSerializer,
            400: 'Bad Request - Invalid CSV format or data'
        }
    )
    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        """
        Upload and process a CSV file containing equipment data.
        Automatically manages dataset history (keeps last 5).
        """
        serializer = CSVUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = serializer.validated_data['file']
        
        # Parse CSV file
        df, error_msg = parse_csv_file(uploaded_file)
        if df is None:
            return Response(
                {'success': False, 'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Analyze data
        analysis = analyze_equipment_data(df)
        
        # Create dataset
        dataset = Dataset.objects.create(
            user=request.user,
            filename=uploaded_file.name,
            file=uploaded_file,
            total_count=analysis['total_count'],
            avg_flowrate=analysis['avg_flowrate'],
            avg_pressure=analysis['avg_pressure'],
            avg_temperature=analysis['avg_temperature'],
            equipment_type_distribution=analysis['equipment_type_distribution'],
            raw_data=convert_dataframe_to_list(df)
        )
        
        # Create equipment data entries
        equipment_items = []
        for _, row in df.iterrows():
            equipment_items.append(EquipmentData(
                dataset=dataset,
                equipment_name=row['Equipment Name'],
                equipment_type=row['Type'],
                flowrate=row['Flowrate'],
                pressure=row['Pressure'],
                temperature=row['Temperature']
            ))
        
        EquipmentData.objects.bulk_create(equipment_items)
        
        # Manage dataset history - keep only last 5
        user_datasets = Dataset.objects.filter(user=request.user).order_by('-uploaded_at')
        if user_datasets.count() > settings.MAX_STORED_DATASETS:
            datasets_to_delete = user_datasets[settings.MAX_STORED_DATASETS:]
            for old_dataset in datasets_to_delete:
                # Delete associated file
                if old_dataset.file:
                    old_dataset.file.delete()
                old_dataset.delete()
        
        # Return created dataset with full details
        response_serializer = DatasetSerializer(dataset)
        return Response(
            {
                'success': True,
                'message': 'CSV file uploaded and processed successfully',
                'data': response_serializer.data,
                'analysis': analysis
            },
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        method='get',
        responses={200: DatasetSummarySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get upload history (last 5 datasets with summaries).
        """
        datasets = self.get_queryset()[:settings.MAX_STORED_DATASETS]
        serializer = DatasetSummarySerializer(datasets, many=True)
        return Response({
            'success': True,
            'count': len(serializer.data),
            'data': serializer.data
        })
    
    @swagger_auto_schema(
        method='get',
        responses={
            200: 'PDF file',
            404: 'Dataset not found'
        }
    )
    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """
        Generate and download a PDF report for a specific dataset.
        """
        dataset = self.get_object()
        
        # Create media directory if it doesn't exist
        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate PDF
        pdf_filename = f"report_{dataset.id}_{dataset.filename.replace('.csv', '')}.pdf"
        pdf_path = os.path.join(reports_dir, pdf_filename)
        
        success = generate_pdf_report(dataset, pdf_path)
        
        if not success:
            return Response(
                {'success': False, 'error': 'Failed to generate PDF report'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Return PDF file
        try:
            return FileResponse(
                open(pdf_path, 'rb'),
                content_type='application/pdf',
                as_attachment=True,
                filename=pdf_filename
            )
        except Exception as e:
            return Response(
                {'success': False, 'error': f'Failed to serve PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        method='get',
        responses={200: openapi.Response('Dataset summary with analysis')}
    )
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Get detailed summary and analysis for a specific dataset.
        """
        dataset = self.get_object()
        serializer = self.get_serializer(dataset)
        
        # Recreate analysis from stored data
        df_dict = dataset.raw_data
        import pandas as pd
        df = pd.DataFrame(df_dict)
        
        analysis = analyze_equipment_data(df)
        
        return Response({
            'success': True,
            'dataset': serializer.data,
            'analysis': analysis
        })


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet for authentication operations.
    Handles user registration, login, and logout.
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        method='post',
        request_body=UserRegistrationSerializer,
        responses={201: UserSerializer}
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user and return auth token."""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={200: 'Login successful with token'}
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Authenticate user and return auth token."""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'success': False, 'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {'success': False, 'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'token': token.key
        })
    
    @swagger_auto_schema(
        method='post',
        responses={200: 'Logout successful'}
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """Logout user by deleting auth token."""
        try:
            request.user.auth_token.delete()
            return Response({
                'success': True,
                'message': 'Logout successful'
            })
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        method='get',
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user information."""
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'user': serializer.data
        })


@swagger_auto_schema(
    method='get',
    responses={200: 'API health check'}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Simple health check endpoint."""
    return Response({
        'status': 'healthy',
        'message': 'Chemical Equipment Visualizer API is running'
    })
