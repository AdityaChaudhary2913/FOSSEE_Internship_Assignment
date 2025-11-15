import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { datasetAPI } from '../services/api';
import { toast } from 'react-toastify';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title, PointElement, LineElement } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title, PointElement, LineElement);

const DatasetDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [dataset, setDataset] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchDatasetDetails();
  }, [id]);

  const fetchDatasetDetails = async () => {
    try {
      const response = await datasetAPI.getSummary(id);
      setDataset(response.dataset);
      setAnalysis(response.analysis);
    } catch (error) {
      toast.error('Failed to load dataset details');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    setDownloading(true);
    try {
      const pdfBlob = await datasetAPI.generatePDF(id);
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `report_${dataset.filename.replace('.csv', '')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('PDF downloaded successfully');
    } catch (error) {
      toast.error('Failed to generate PDF');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading dataset details...</p>
      </div>
    );
  }

  if (!dataset || !analysis) {
    return null;
  }

  // Prepare chart data
  const typeDistributionData = {
    labels: Object.keys(analysis.equipment_type_distribution),
    datasets: [{
      data: Object.values(analysis.equipment_type_distribution),
      backgroundColor: [
        '#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9C27B0',
        '#00BCD4', '#FFEB3B', '#795548', '#607D8B'
      ],
    }],
  };

  const avgParametersData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [{
      label: 'Average Values',
      data: [analysis.avg_flowrate, analysis.avg_pressure, analysis.avg_temperature],
      backgroundColor: ['#4CAF50', '#2196F3', '#FF9800'],
    }],
  };

  const parameterRangesData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [
      {
        label: 'Minimum',
        data: [analysis.min_flowrate, analysis.min_pressure, analysis.min_temperature],
        backgroundColor: '#FF9800',
      },
      {
        label: 'Average',
        data: [analysis.avg_flowrate, analysis.avg_pressure, analysis.avg_temperature],
        backgroundColor: '#4CAF50',
      },
      {
        label: 'Maximum',
        data: [analysis.max_flowrate, analysis.max_pressure, analysis.max_temperature],
        backgroundColor: '#2196F3',
      },
    ],
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>{dataset.filename}</h1>
          <p>Uploaded on {new Date(dataset.uploaded_at).toLocaleString()}</p>
        </div>
        <button onClick={handleDownloadPDF} className="btn btn-primary" disabled={downloading}>
          {downloading ? 'Generating PDF...' : '📄 Download PDF Report'}
        </button>
      </div>

      <div className="grid grid-3">
        <div className="stats-card">
          <h3>Total Equipment</h3>
          <div className="value">{analysis.total_count}</div>
        </div>
        <div className="stats-card secondary">
          <h3>Equipment Types</h3>
          <div className="value">{Object.keys(analysis.equipment_type_distribution).length}</div>
        </div>
        <div className="stats-card warning">
          <h3>Avg Flowrate</h3>
          <div className="value">{analysis.avg_flowrate.toFixed(2)}</div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h2>Equipment Type Distribution</h2>
          <div className="chart-container" style={{ height: '300px' }}>
            <Pie data={typeDistributionData} options={{ maintainAspectRatio: false }} />
          </div>
        </div>

        <div className="card">
          <h2>Average Parameters</h2>
          <div className="chart-container" style={{ height: '300px' }}>
            <Bar 
              data={avgParametersData}
              options={{
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
              }}
            />
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Parameter Ranges (Min / Avg / Max)</h2>
        <div className="chart-container">
          <Bar
            data={parameterRangesData}
            options={{
              maintainAspectRatio: false,
              plugins: { title: { display: false } }
            }}
          />
        </div>
      </div>

      <div className="card">
        <h2>Statistics by Equipment Type</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Equipment Type</th>
              <th>Count</th>
              <th>Avg Flowrate</th>
              <th>Avg Pressure</th>
              <th>Avg Temperature</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(analysis.statistics_by_type).map(([type, stats]) => (
              <tr key={type}>
                <td><strong>{type}</strong></td>
                <td>{stats.count}</td>
                <td>{stats.avg_flowrate.toFixed(2)}</td>
                <td>{stats.avg_pressure.toFixed(2)}</td>
                <td>{stats.avg_temperature.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {dataset.equipment_items && dataset.equipment_items.length > 0 && (
        <div className="card">
          <h2>All Equipment Data</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>Equipment Name</th>
                <th>Type</th>
                <th>Flowrate</th>
                <th>Pressure</th>
                <th>Temperature</th>
              </tr>
            </thead>
            <tbody>
              {dataset.equipment_items.map((item, index) => (
                <tr key={index}>
                  <td>{item.equipment_name}</td>
                  <td>{item.equipment_type}</td>
                  <td>{item.flowrate}</td>
                  <td>{item.pressure}</td>
                  <td>{item.temperature}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default DatasetDetail;
