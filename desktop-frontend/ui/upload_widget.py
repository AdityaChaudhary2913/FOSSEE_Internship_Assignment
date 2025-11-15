"""Upload Widget - CSV file upload interface"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal

class UploadWidget(QWidget):
    upload_success = pyqtSignal(int)
    
    def __init__(self, api_service):
        super().__init__()
        self.api_service = api_service
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Select a CSV file to upload")
        layout.addWidget(self.status_label)
        
        select_btn = QPushButton("Select CSV File")
        select_btn.clicked.connect(self.select_file)
        layout.addWidget(select_btn)
        
        self.upload_btn = QPushButton("Upload")
        self.upload_btn.clicked.connect(self.upload_file)
        self.upload_btn.setEnabled(False)
        layout.addWidget(self.upload_btn)
        
        layout.addStretch()
        self.setLayout(layout)
        self.selected_file = None
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.selected_file = file_path
            self.status_label.setText(f"Selected: {file_path}")
            self.upload_btn.setEnabled(True)
    
    def upload_file(self):
        if not self.selected_file:
            return
        
        try:
            result = self.api_service.upload_csv(self.selected_file)
            dataset_id = result['data']['id']
            self.upload_success.emit(dataset_id)
            self.selected_file = None
            self.upload_btn.setEnabled(False)
            self.status_label.setText("Upload successful!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")
