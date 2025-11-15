import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { datasetAPI } from '../services/api';
import { toast } from 'react-toastify';
import './Upload.css';

const Upload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        toast.error('Please select a CSV file');
        return;
      }
      if (selectedFile.size > 5 * 1024 * 1024) {
        toast.error('File size must not exceed 5MB');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      if (!droppedFile.name.endsWith('.csv')) {
        toast.error('Please select a CSV file');
        return;
      }
      setFile(droppedFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const response = await datasetAPI.uploadCSV(file, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(progress);
      });

      toast.success(response.message || 'File uploaded successfully!');
      navigate(`/dataset/${response.data.id}`);
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Upload failed';
      toast.error(errorMsg);
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setUploadProgress(0);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Upload CSV File</h1>
        <p>Upload a CSV file containing equipment data for analysis</p>
      </div>

      <div className="card">
        <div className="upload-requirements">
          <h3>CSV File Requirements</h3>
          <ul>
            <li>File must be in CSV format (.csv extension)</li>
            <li>Maximum file size: 5MB</li>
            <li>Required columns: Equipment Name, Type, Flowrate, Pressure, Temperature</li>
            <li>All numeric columns must contain valid numbers</li>
            <li>No empty values in required columns</li>
          </ul>
        </div>

        <div
          className={`drop-zone ${file ? 'has-file' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {file ? (
            <div className="file-info">
              <span className="file-icon">📄</span>
              <div className="file-details">
                <p className="file-name">{file.name}</p>
                <p className="file-size">{(file.size / 1024).toFixed(2)} KB</p>
              </div>
              <button onClick={handleReset} className="btn-remove" disabled={uploading}>
                ✕
              </button>
            </div>
          ) : (
            <div className="drop-zone-content">
              <span className="upload-icon">☁️</span>
              <p className="drop-zone-text">Drag and drop your CSV file here</p>
              <p className="drop-zone-or">or</p>
              <label className="btn btn-primary">
                Browse Files
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                />
              </label>
            </div>
          )}
        </div>

        {uploading && (
          <div className="upload-progress">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
            </div>
            <p className="progress-text">{uploadProgress}%</p>
          </div>
        )}

        <div className="upload-actions">
          <button
            onClick={handleUpload}
            className="btn btn-primary"
            disabled={!file || uploading}
          >
            {uploading ? 'Uploading...' : 'Upload and Analyze'}
          </button>
          {file && !uploading && (
            <button onClick={handleReset} className="btn btn-secondary">
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="card">
        <h3>Sample Data Format</h3>
        <div className="sample-csv">
          <pre>
            Equipment Name,Type,Flowrate,Pressure,Temperature{'\n'}
            Pump-1,Pump,120,5.2,110{'\n'}
            Compressor-1,Compressor,95,8.4,95{'\n'}
            Valve-1,Valve,60,4.1,105
          </pre>
        </div>
      </div>
    </div>
  );
};

export default Upload;
