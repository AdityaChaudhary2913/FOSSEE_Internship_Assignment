"""Login Dialog for Desktop Application"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QMessageBox, QTabWidget, QWidget, QFormLayout)
from PyQt5.QtCore import Qt


class LoginDialog(QDialog):
    """Dialog for user authentication"""
    
    def __init__(self, api_service, parent=None):
        super().__init__(parent)
        self.api_service = api_service
        self.user_data = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Login")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Tabs for login/register
        tabs = QTabWidget()
        tabs.addTab(self.create_login_tab(), "Login")
        tabs.addTab(self.create_register_tab(), "Register")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def create_login_tab(self):
        """Create login tab"""
        widget = QWidget()
        layout = QFormLayout()
        
        self.login_username = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        
        layout.addRow("Username:", self.login_username)
        layout.addRow("Password:", self.login_password)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.do_login)
        layout.addRow(login_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_register_tab(self):
        """Create registration tab"""
        widget = QWidget()
        layout = QFormLayout()
        
        self.reg_username = QLineEdit()
        self.reg_email = QLineEdit()
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password_confirm = QLineEdit()
        self.reg_password_confirm.setEchoMode(QLineEdit.Password)
        
        layout.addRow("Username:", self.reg_username)
        layout.addRow("Email:", self.reg_email)
        layout.addRow("Password:", self.reg_password)
        layout.addRow("Confirm Password:", self.reg_password_confirm)
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.do_register)
        layout.addRow(register_btn)
        
        widget.setLayout(layout)
        return widget
    
    def do_login(self):
        """Handle login"""
        username = self.login_username.text()
        password = self.login_password.text()
        
        try:
            result = self.api_service.login(username, password)
            self.user_data = result.get('user')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")
    
    def do_register(self):
        """Handle registration"""
        if self.reg_password.text() != self.reg_password_confirm.text():
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        user_data = {
            'username': self.reg_username.text(),
            'email': self.reg_email.text(),
            'password': self.reg_password.text(),
            'password_confirm': self.reg_password_confirm.text()
        }
        
        try:
            result = self.api_service.register(user_data)
            self.user_data = result.get('user')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {str(e)}")
