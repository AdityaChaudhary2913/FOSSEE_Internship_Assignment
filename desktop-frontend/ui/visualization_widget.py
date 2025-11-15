"""Visualization Widget - Display charts with Matplotlib"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class VisualizationWidget(QWidget):
    def __init__(self, api_service):
        super().__init__()
        self.api_service = api_service
        self.current_dataset = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.info_label = QLabel("Select a dataset from history to visualize")
        layout.addWidget(self.info_label)
        
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        pdf_btn = QPushButton("Download PDF Report")
        pdf_btn.clicked.connect(self.download_pdf)
        layout.addWidget(pdf_btn)
        
        self.setLayout(layout)
    
    def load_dataset(self, dataset_id):
        try:
            result = self.api_service.get_dataset_summary(dataset_id)
            self.current_dataset = result
            self.info_label.setText(f"Dataset: {result['dataset']['filename']}")
            self.plot_charts(result['analysis'])
        except Exception as e:
            self.info_label.setText(f"Error loading dataset: {e}")
    
    def plot_charts(self, analysis):
        self.figure.clear()
        
        ax1 = self.figure.add_subplot(121)
        types = list(analysis['equipment_type_distribution'].keys())
        counts = list(analysis['equipment_type_distribution'].values())
        ax1.pie(counts, labels=types, autopct='%1.1f%%')
        ax1.set_title('Equipment Type Distribution')
        
        ax2 = self.figure.add_subplot(122)
        params = ['Flowrate', 'Pressure', 'Temperature']
        values = [analysis['avg_flowrate'], analysis['avg_pressure'], analysis['avg_temperature']]
        ax2.bar(params, values, color=['#4CAF50', '#2196F3', '#FF9800'])
        ax2.set_title('Average Parameters')
        ax2.set_ylabel('Value')
        
        self.canvas.draw()
    
    def download_pdf(self):
        if not self.current_dataset:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                dataset_id = self.current_dataset['dataset']['id']
                self.api_service.download_pdf(dataset_id, file_path)
                self.info_label.setText(f"PDF saved to {file_path}")
            except Exception as e:
                self.info_label.setText(f"Error downloading PDF: {e}")
