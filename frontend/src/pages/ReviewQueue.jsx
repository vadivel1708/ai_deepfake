import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { UserCheck, Eye, RefreshCw, AlertCircle, FileCheck, CheckCircle2 } from 'lucide-react';
import { reviewAPI } from '../services/api';

export default function ReviewQueue() {
  const [loading, setLoading] = useState(true);
  const [reviews, setReviews] = useState([]);
  const [error, setError] = useState('');

  const fetchReviews = async () => {
    setLoading(true);
    try {
      const res = await reviewAPI.getPending();
      setReviews(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load review queue.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
  }, []);

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span className="badge badge-cyan">FORENSIC TRIAGE</span>
            <h1 style={{ fontSize: '1.85rem' }}>Human Review Queue</h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Cases flagged as suspicious, borderline, or awaiting expert forensic determination
          </p>
        </div>
        <button onClick={fetchReviews} className="btn btn-secondary">
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh Queue
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

      <div className="card">
        {reviews.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '4rem 1rem', color: 'var(--text-muted)' }}>
            <FileCheck size={48} color="var(--emerald-safe)" style={{ margin: '0 auto 1rem', opacity: 0.6 }} />
            <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>All Cases Reviewed</h3>
            <p style={{ fontSize: '0.875rem' }}>No media items currently pending human reviewer assessment.</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '0.75rem 0.5rem' }}>File Name</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Media Type</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>AI Prediction</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>AI Likelihood</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Reviewer Notes</th>
                  <th style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {reviews.map((r) => (
                  <tr key={r.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '0.875rem 0.5rem', fontWeight: 600 }}>
                      {r.original_filename || r.analysis_id.slice(0, 12)}
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem', textTransform: 'uppercase', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {r.media_type || 'MEDIA'}
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem' }}>
                      <span className={`badge ${r.ai_prediction === 'likely_authentic' ? 'badge-authentic' : (r.ai_prediction === 'potentially_manipulated' ? 'badge-manipulated' : 'badge-inconclusive')}`}>
                        {(r.ai_prediction || 'PENDING').replace('_', ' ')}
                      </span>
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem', fontFamily: 'var(--font-mono)' }}>
                      {r.ai_confidence !== null && r.ai_confidence !== undefined
                        ? `${(r.ai_confidence * 100).toFixed(1)}%`
                        : '—'}
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem', color: 'var(--text-secondary)', maxWidth: '240px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {r.notes || 'Awaiting initial assessment.'}
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem', textAlign: 'right' }}>
                      <Link
                        to={`/analysis/${r.analysis_id}`}
                        className="btn btn-primary"
                        style={{ padding: '0.35rem 0.85rem', fontSize: '0.775rem' }}
                      >
                        <Eye size={14} />
                        Review Evidence
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
