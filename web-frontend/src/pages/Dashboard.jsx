import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { datasetAPI } from '../services/api';
import { toast } from 'react-toastify';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const Dashboard = () => {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await datasetAPI.getHistory();
      setDatasets(response.data || []);
      
      if (response.data && response.data.length > 0) {
        calculateStats(response.data);
      }
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (data) => {
    const totalDatasets = data.length;
    const totalEquipment = data.reduce((sum, ds) => sum + ds.total_count, 0);
    const avgFlowrate = data.reduce((sum, ds) => sum + (ds.avg_flowrate || 0), 0) / totalDatasets;

    setStats({
      totalDatasets,
      totalEquipment,
      avgFlowrate: avgFlowrate.toFixed(2),
    });
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your equipment data</p>
      </div>

      {stats && (
        <div className="grid grid-3">
          <div className="stats-card">
            <h3>Total Datasets</h3>
            <div className="value">{stats.totalDatasets}</div>
          </div>
          <div className="stats-card secondary">
            <h3>Total Equipment</h3>
            <div className="value">{stats.totalEquipment}</div>
          </div>
          <div className="stats-card warning">
            <h3>Avg Flowrate</h3>
            <div className="value">{stats.avgFlowrate}</div>
          </div>
        </div>
      )}

      <div className="card">
        <h2>Recent Uploads</h2>
        {datasets.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <p>No datasets uploaded yet.</p>
            <Link to="/upload" className="btn btn-primary" style={{ marginTop: '16px' }}>
              Upload Your First Dataset
            </Link>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Equipment Count</th>
                <th>Avg Flowrate</th>
                <th>Avg Pressure</th>
                <th>Avg Temperature</th>
                <th>Uploaded</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((dataset) => (
                <tr key={dataset.id}>
                  <td>{dataset.filename}</td>
                  <td>{dataset.total_count}</td>
                  <td>{dataset.avg_flowrate?.toFixed(2)}</td>
                  <td>{dataset.avg_pressure?.toFixed(2)}</td>
                  <td>{dataset.avg_temperature?.toFixed(2)}</td>
                  <td>{new Date(dataset.uploaded_at).toLocaleDateString()}</td>
                  <td>
                    <Link to={`/dataset/${dataset.id}`} className="btn btn-secondary" style={{ fontSize: '12px', padding: '6px 12px' }}>
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
