import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { datasetAPI } from '../services/api';
import { toast } from 'react-toastify';

const History = () => {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await datasetAPI.getHistory();
      setDatasets(response.data || []);
    } catch (error) {
      toast.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this dataset?')) {
      return;
    }

    try {
      await datasetAPI.deleteDataset(id);
      toast.success('Dataset deleted successfully');
      setDatasets(datasets.filter(ds => ds.id !== id));
    } catch (error) {
      toast.error('Failed to delete dataset');
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading history...</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Upload History</h1>
        <p>View and manage your last 5 uploaded datasets</p>
      </div>

      {datasets.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <h3>No datasets found</h3>
          <p>Upload your first CSV file to get started</p>
          <Link to="/upload" className="btn btn-primary" style={{ marginTop: '16px' }}>
            Upload Dataset
          </Link>
        </div>
      ) : (
        <div className="grid">
          {datasets.map((dataset) => (
            <div key={dataset.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ margin: '0 0 8px 0' }}>{dataset.filename}</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: 0 }}>
                    Uploaded on {new Date(dataset.uploaded_at).toLocaleString()}
                  </p>
                </div>
                <span style={{ 
                  backgroundColor: 'var(--primary-color)', 
                  color: 'white', 
                  padding: '4px 12px', 
                  borderRadius: '12px',
                  fontSize: '14px',
                  fontWeight: '500'
                }}>
                  {dataset.total_count} items
                </span>
              </div>

              <div className="grid grid-3" style={{ marginBottom: '20px' }}>
                <div>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '0 0 4px 0' }}>Avg Flowrate</p>
                  <p style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>{dataset.avg_flowrate?.toFixed(2)}</p>
                </div>
                <div>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '0 0 4px 0' }}>Avg Pressure</p>
                  <p style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>{dataset.avg_pressure?.toFixed(2)}</p>
                </div>
                <div>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '0 0 4px 0' }}>Avg Temperature</p>
                  <p style={{ fontSize: '18px', fontWeight: '600', margin: 0 }}>{dataset.avg_temperature?.toFixed(2)}</p>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <Link to={`/dataset/${dataset.id}`} className="btn btn-primary" style={{ flex: 1 }}>
                  View Details
                </Link>
                <button 
                  onClick={() => handleDelete(dataset.id)} 
                  className="btn btn-danger"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
