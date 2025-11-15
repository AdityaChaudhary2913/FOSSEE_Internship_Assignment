"""
API Service for Desktop Application
Handles all communication with Django backend
"""

import requests
import json
from typing import Optional, Dict, Any


class APIService:
    """Service class for API communication"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication token"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and store token"""
        url = f"{self.base_url}/auth/login/"
        data = {"username": username, "password": password}
        response = self.session.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        self.token = result.get("token")
        return result
    
    def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        url = f"{self.base_url}/auth/register/"
        response = self.session.post(url, json=user_data)
        response.raise_for_status()
        result = response.json()
        self.token = result.get("token")
        return result
    
    def logout(self) -> None:
        """Logout user"""
        if self.token:
            url = f"{self.base_url}/auth/logout/"
            try:
                self.session.post(url, headers=self._get_headers())
            finally:
                self.token = None
    
    def upload_csv(self, file_path: str) -> Dict[str, Any]:
        """Upload CSV file"""
        url = f"{self.base_url}/datasets/upload_csv/"
        headers = {}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(url, files=files, headers=headers)
        
        response.raise_for_status()
        return response.json()
    
    def get_history(self) -> Dict[str, Any]:
        """Get dataset history"""
        url = f"{self.base_url}/datasets/history/"
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_dataset_summary(self, dataset_id: int) -> Dict[str, Any]:
        """Get detailed dataset summary"""
        url = f"{self.base_url}/datasets/{dataset_id}/summary/"
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def download_pdf(self, dataset_id: int, save_path: str) -> None:
        """Download PDF report"""
        url = f"{self.base_url}/datasets/{dataset_id}/generate_pdf/"
        response = self.session.get(url, headers=self._get_headers(), stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
