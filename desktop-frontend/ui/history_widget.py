"""History Widget - Display dataset history"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import pyqtSignal

class HistoryWidget(QWidget):
    dataset_selected = pyqtSignal(int)
    
    def __init__(self, api_service):
        super().__init__()
        self.api_service = api_service
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Filename', 'Count', 'Avg Flowrate', 'Date'])
        self.table.cellDoubleClicked.connect(self.on_row_selected)
        layout.addWidget(self.table)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_history)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
    
    def load_history(self):
        try:
            result = self.api_service.get_history()
            datasets = result.get('data', [])
            self.table.setRowCount(len(datasets))
            
            for i, ds in enumerate(datasets):
                self.table.setItem(i, 0, QTableWidgetItem(ds['filename']))
                self.table.setItem(i, 1, QTableWidgetItem(str(ds['total_count'])))
                self.table.setItem(i, 2, QTableWidgetItem(f"{ds['avg_flowrate']:.2f}"))
                self.table.setItem(i, 3, QTableWidgetItem(ds['uploaded_at'][:10]))
                self.table.item(i, 0).setData(100, ds['id'])
        except Exception as e:
            print(f"Failed to load history: {e}")
    
    def on_row_selected(self, row, col):
        dataset_id = self.table.item(row, 0).data(100)
        self.dataset_selected.emit(dataset_id)
