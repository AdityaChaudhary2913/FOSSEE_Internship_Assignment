"""
Main Window for Chemical Equipment Visualizer Desktop Application
Implements MVC pattern with PyQt5
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTabWidget, QMessageBox,
                             QFileDialog, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import os

from services.api_service import APIService
from ui.login_dialog import LoginDialog
from ui.upload_widget import UploadWidget
from ui.history_widget import HistoryWidget
from ui.visualization_widget import VisualizationWidget


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.api_service = APIService()
        self.current_user = None
        self.init_ui()
        self.show_login()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Header
        self.create_header()
        
        # Tab widget
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.upload_widget = UploadWidget(self.api_service)
        self.history_widget = HistoryWidget(self.api_service)
        self.visualization_widget = VisualizationWidget(self.api_service)
        
        self.tabs.addTab(self.upload_widget, "Upload CSV")
        self.tabs.addTab(self.history_widget, "History")
        self.tabs.addTab(self.visualization_widget, "Visualization")
        
        # Connect signals
        self.upload_widget.upload_success.connect(self.on_upload_success)
        self.history_widget.dataset_selected.connect(self.on_dataset_selected)
        
        # Initially disable tabs until login
        self.set_tabs_enabled(False)
    
    def create_header(self):
        """Create application header"""
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("⚗️ Chemical Equipment Visualizer")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # User label
        self.user_label = QLabel("")
        header_layout.addWidget(self.user_label)
        
        # Logout button
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        self.logout_btn.setVisible(False)
        header_layout.addWidget(self.logout_btn)
        
        self.main_layout.addLayout(header_layout)
    
    def show_login(self):
        """Show login dialog"""
        dialog = LoginDialog(self.api_service, self)
        if dialog.exec_():
            self.current_user = dialog.user_data
            self.on_login_success()
        else:
            # User closed dialog without logging in
            QMessageBox.information(self, "Info", "Please login to use the application")
            self.close()
    
    def on_login_success(self):
        """Handle successful login"""
        username = self.current_user.get('username', 'User')
        self.user_label.setText(f"Welcome, {username}")
        self.logout_btn.setVisible(True)
        self.set_tabs_enabled(True)
        self.history_widget.load_history()
    
    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(self, 'Logout', 
                                    'Are you sure you want to logout?',
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.api_service.logout()
            self.current_user = None
            self.user_label.setText("")
            self.logout_btn.setVisible(False)
            self.set_tabs_enabled(False)
            self.show_login()
    
    def set_tabs_enabled(self, enabled: bool):
        """Enable or disable all tabs"""
        self.tabs.setEnabled(enabled)
    
    def on_upload_success(self, dataset_id: int):
        """Handle successful file upload"""
        QMessageBox.information(self, "Success", "File uploaded successfully!")
        self.history_widget.load_history()
        self.tabs.setCurrentWidget(self.visualization_widget)
        self.visualization_widget.load_dataset(dataset_id)
    
    def on_dataset_selected(self, dataset_id: int):
        """Handle dataset selection from history"""
        self.tabs.setCurrentWidget(self.visualization_widget)
        self.visualization_widget.load_dataset(dataset_id)
