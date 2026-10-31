import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  Trash2, 
  RefreshCw, 
  Eye, 
  AlertCircle, 
  ChevronLeft, 
  ChevronRight,
  FileCheck2,
  Calendar
} from 'lucide-react';
import { analysisAPI, mediaAPI } from '../services/api';

export default function AnalysisHistory() {
  const [loading, setLoading] = useState(true);
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const limit = 15;

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [mediaTypeFilter, setMediaTypeFilter] = useState('');
  const [predictionFilter, setPredictionFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [error, setError] = useState('');

  const fetchHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const params = {
        skip: page * limit,
        limit,
        query: searchQuery || undefined,
        media_type: mediaTypeFilter || undefined,
        prediction: predictionFilter || undefined,
        status: statusFilter || undefined,
      };
      const res = await analysisAPI.getHistory(params);
      setItems(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      setError('Could not load analysis records: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, mediaTypeFilter, predictionFilter, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    fetchHistory();
  };

  const handleDelete = async (mediaId, analysisId) => {
    if (!window.confirm('Are you sure you want to delete this analysis record and its associated storage files?')) return;
    try {
      await mediaAPI.deleteMedia(mediaId);
      fetchHistory();
    } catch (err) {
      alert('Delete failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRetry = async (analysisId) => {
    try {
      await analysisAPI.retry(analysisId);
      fetchHistory();
    } catch (err) {
      alert('Retry failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.85rem', marginBottom: '0.25rem' }}>Forensic Audit & Analysis History</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Query past investigations, filter by confidence thresholds, or export historical dossiers
          </p>
        </div>
        <button onClick={fetchHistory} className="btn btn-secondary">
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {error && (
        <div style={{
          padding: '0.875rem 1rem',
          background: 'rgba(244, 63, 94, 0.1)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          borderRadius: 'var(--radius-sm)',
          color: '#fb7185',
          fontSize: '0.85rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '1.5rem'
        }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="card" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
          <div style={{ flex: '1 1 240px', position: 'relative' }}>
            <input
              type="text"
              placeholder="Search filename or Analysis ID..."
              className="input-control"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '2.5rem' }}
            />
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
          </div>

          <div style={{ flex: '0 1 160px' }}>
            <select
              className="select-control"
              value={mediaTypeFilter}
              onChange={(e) => { setMediaTypeFilter(e.target.value); setPage(0); }}
            >
              <option value="">All Media Types</option>
              <option value="image">Images</option>
              <option value="video">Videos</option>
              <option value="audio">Audio</option>
            </select>
          </div>

          <div style={{ flex: '0 1 180px' }}>
            <select
              className="select-control"
              value={predictionFilter}
              onChange={(e) => { setPredictionFilter(e.target.value); setPage(0); }}
            >
              <option value="">All Predictions</option>
              <option value="likely_authentic">Likely Authentic</option>
              <option value="potentially_manipulated">Potentially Manipulated</option>
              <option value="inconclusive">Inconclusive</option>
            </select>
          </div>

          <div style={{ flex: '0 1 150px' }}>
            <select
              className="select-control"
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
            >
              <option value="">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary" style={{ padding: '0.625rem 1.25rem' }}>
            Filter
          </button>
        </form>
      </div>

      {/* History Table */}
      <div className="card" style={{ padding: '1.25rem' }}>
        {items.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            <p>No matching analysis records found.</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '0.75rem 0.5rem' }}>File Name / ID</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Type</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>AI Prediction</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Likelihood</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Created At</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Status</th>
                  <th style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((j) => (
                  <tr key={j.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '0.875rem 0.5rem' }}>
                      <div style={{ fontWeight: 600 }}>{j.original_filename || 'Unknown'}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        {j.id.slice(0, 16)}...
                      </div>
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem', textTransform: 'uppercase', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {j.media_type || 'MEDIA'}
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem' }}>
                      {j.prediction ? (
                        <span className={`badge ${j.prediction === 'likely_authentic' ? 'badge-authentic' : (j.prediction === 'potentially_manipulated' ? 'badge-manipulated' : 'badge-inconclusive')}`}>
                          {j.prediction.replace('_', ' ')}
                        </span>
                      ) : (
                        <span className="badge badge-pending">PENDING</span>
                      )}
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem', fontFamily: 'var(--font-mono)' }}>
                      {j.confidence_score !== null && j.confidence_score !== undefined
                        ? `${(j.confidence_score * 100).toFixed(1)}%`
                        : '—'}
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem', color: 'var(--text-muted)', fontSize: '0.775rem' }}>
                      {new Date(j.created_at).toLocaleDateString()} {new Date(j.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem' }}>
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        color: j.status === 'completed' ? 'var(--emerald-safe)' : (j.status === 'failed' ? 'var(--rose-danger)' : 'var(--cyan-primary)')
                      }}>
                        {j.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem', textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                        <Link
                          to={`/analysis/${j.id}`}
                          className="btn btn-secondary"
                          style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                          title="Inspect Evidence"
                        >
                          <Eye size={14} />
                        </Link>
                        {j.status === 'failed' && (
                          <button
                            onClick={() => handleRetry(j.id)}
                            className="btn btn-secondary"
                            style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                            title="Retry Analysis"
                          >
                            <RefreshCw size={14} />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(j.media_id, j.id)}
                          className="btn btn-danger"
                          style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                          title="Authorized Deletion"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.85rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>
              Page {page + 1} of {totalPages} ({total} total analyses)
            </span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                disabled={page === 0}
                onClick={() => setPage(page - 1)}
                className="btn btn-secondary"
                style={{ padding: '0.4rem 0.75rem' }}
              >
                <ChevronLeft size={16} />
                Previous
              </button>
              <button
                disabled={page >= totalPages - 1}
                onClick={() => setPage(page + 1)}
                className="btn btn-secondary"
                style={{ padding: '0.4rem 0.75rem' }}
              >
                Next
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
