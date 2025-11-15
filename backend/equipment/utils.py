"""
Utility functions for the Equipment application.
Includes CSV parsing, data analysis, PDF generation, and error handling.
"""

import pandas as pd
import io
from typing import Dict, Any, List, Tuple
from django.core.files.uploadedfile import UploadedFile
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides detailed error messages.
    Follows REST API best practices for error responses.
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        errors = []
        if isinstance(response.data, dict):
            for field, value in response.data.items():
                if isinstance(value, list):
                    errors.extend([f"{field}: {error}" for error in value])
                else:
                    errors.append(f"{field}: {value}")
        else:
            errors = [str(response.data)]
        
        response.data = {
            'success': False,
            'errors': errors,
            'status_code': response.status_code
        }
    
    return response


def validate_csv_structure(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that the CSV has the required columns and data types.
    
    Args:
        df: Pandas DataFrame to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
    
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check for empty dataframe
    if df.empty:
        return False, "CSV file is empty"
    
    # Validate data types for numeric columns
    numeric_columns = ['Flowrate', 'Pressure', 'Temperature']
    for col in numeric_columns:
        try:
            pd.to_numeric(df[col], errors='raise')
        except (ValueError, TypeError):
            return False, f"Column '{col}' must contain numeric values"
    
    # Check for null values in required columns
    null_counts = df[required_columns].isnull().sum()
    columns_with_nulls = null_counts[null_counts > 0].index.tolist()
    if columns_with_nulls:
        return False, f"Null values found in columns: {', '.join(columns_with_nulls)}"
    
    return True, ""


def parse_csv_file(file: UploadedFile) -> Tuple[pd.DataFrame, str]:
    """
    Parse uploaded CSV file into a pandas DataFrame.
    
    Args:
        file: Uploaded CSV file
        
    Returns:
        Tuple of (DataFrame, error_message)
    """
    try:
        # Read CSV file
        content = file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # Validate structure
        is_valid, error_msg = validate_csv_structure(df)
        if not is_valid:
            return None, error_msg
        
        # Clean data
        df = df.dropna(subset=['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        
        # Ensure numeric columns are properly typed
        df['Flowrate'] = pd.to_numeric(df['Flowrate'])
        df['Pressure'] = pd.to_numeric(df['Pressure'])
        df['Temperature'] = pd.to_numeric(df['Temperature'])
        
        return df, ""
    
    except pd.errors.EmptyDataError:
        return None, "CSV file is empty"
    except pd.errors.ParserError as e:
        return None, f"Error parsing CSV: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error reading CSV: {str(e)}"


def analyze_equipment_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform statistical analysis on equipment data.
    
    Args:
        df: DataFrame containing equipment data
        
    Returns:
        Dictionary with summary statistics
    """
    analysis = {
        'total_count': len(df),
        'avg_flowrate': float(df['Flowrate'].mean()),
        'avg_pressure': float(df['Pressure'].mean()),
        'avg_temperature': float(df['Temperature'].mean()),
        'min_flowrate': float(df['Flowrate'].min()),
        'max_flowrate': float(df['Flowrate'].max()),
        'min_pressure': float(df['Pressure'].min()),
        'max_pressure': float(df['Pressure'].max()),
        'min_temperature': float(df['Temperature'].min()),
        'max_temperature': float(df['Temperature'].max()),
        'equipment_type_distribution': df['Type'].value_counts().to_dict(),
    }
    
    # Add statistics by equipment type
    type_stats = {}
    for equipment_type in df['Type'].unique():
        type_df = df[df['Type'] == equipment_type]
        type_stats[equipment_type] = {
            'count': len(type_df),
            'avg_flowrate': float(type_df['Flowrate'].mean()),
            'avg_pressure': float(type_df['Pressure'].mean()),
            'avg_temperature': float(type_df['Temperature'].mean()),
        }
    
    analysis['statistics_by_type'] = type_stats
    
    return analysis


def generate_pdf_report(dataset, filepath: str) -> bool:
    """
    Generate a PDF report for a dataset with summary statistics and equipment details.
    
    Args:
        dataset: Dataset model instance
        filepath: Path where the PDF should be saved
        
    Returns:
        Boolean indicating success
    """
    try:
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        title = Paragraph("Chemical Equipment Analysis Report", title_style)
        story.append(title)
        story.append(Spacer(1, 0.2 * inch))
        
        # Dataset information
        info_data = [
            ['Dataset Information', ''],
            ['Filename:', dataset.filename],
            ['Upload Date:', dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Equipment Count:', str(dataset.total_count)],
        ]
        
        info_table = Table(info_data, colWidths=[2.5 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Summary Statistics
        story.append(Paragraph("Summary Statistics", heading_style))
        summary_data = [
            ['Parameter', 'Average Value'],
            ['Flowrate', f"{dataset.avg_flowrate:.2f}"],
            ['Pressure', f"{dataset.avg_pressure:.2f}"],
            ['Temperature', f"{dataset.avg_temperature:.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3 * inch, 3.5 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Equipment Type Distribution
        story.append(Paragraph("Equipment Type Distribution", heading_style))
        dist_data = [['Equipment Type', 'Count']]
        for eq_type, count in dataset.equipment_type_distribution.items():
            dist_data.append([eq_type, str(count)])
        
        dist_table = Table(dist_data, colWidths=[3 * inch, 3.5 * inch])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(dist_table)
        
        # Build PDF
        doc.build(story)
        return True
    
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return False


def convert_dataframe_to_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert DataFrame to list of dictionaries for JSON serialization.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        List of dictionaries
    """
    return df.to_dict('records')
