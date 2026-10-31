import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  Users, 
  Cpu, 
  ShieldAlert, 
  Activity, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  RefreshCw,
  Lock,
  Database,
  FileText
} from 'lucide-react';
import { adminAPI } from '../services/api';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('users'); // 'users', 'models', 'audit'
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [modelsList, setModelsList] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const loadAllAdminData = async () => {
    setLoading(true);
    setError('');
    try {
      const [metRes, uRes, mRes, aRes] = await Promise.all([
        adminAPI.getMetrics(),
        adminAPI.getUsers(),
        adminAPI.getModels(),
        adminAPI.getAuditLogs(50)
      ]);
      setMetrics(metRes.data);
      setUsersList(uRes.data || []);
      setModelsList(mRes.data || []);
      setAuditLogs(aRes.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load administrator data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllAdminData();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    try {
      await adminAPI.updateRole(userId, newRole);
      setSuccessMsg(`User role updated to ${newRole}.`);
      setTimeout(() => setSuccessMsg(''), 3000);
      const uRes = await adminAPI.getUsers();
      setUsersList(uRes.data || []);
    } catch (err) {
      alert('Role change failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span className="badge badge-cyan">ADMINISTRATOR CONTROL</span>
            <h1 style={{ fontSize: '1.85rem' }}>System Oversight & Governance</h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            User role authorizations, AI model versioning, and immutable audit logging
          </p>
        </div>
        <button onClick={loadAllAdminData} className="btn btn-secondary">
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

      {successMsg && (
        <div style={{
          padding: '0.75rem 1rem',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--emerald-safe)',
          fontSize: '0.85rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '1.5rem'
        }}>
          <CheckCircle size={18} />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Top System Health Cards */}
      {metrics && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          gap: '1.25rem',
          marginBottom: '2rem'
        }}>
          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Registered Users</div>
            <div style={{ fontSize: '1.85rem', fontWeight: 800, fontFamily: 'var(--font-mono)', marginTop: '0.25rem' }}>
              {metrics.total_users}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Accounts in system</div>
          </div>

          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Ingestions</div>
            <div style={{ fontSize: '1.85rem', fontWeight: 800, fontFamily: 'var(--font-mono)', marginTop: '0.25rem' }}>
              {metrics.total_analyses}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Processed media jobs</div>
          </div>

          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Failure Rate</div>
            <div style={{ fontSize: '1.85rem', fontWeight: 800, fontFamily: 'var(--font-mono)', marginTop: '0.25rem', color: metrics.failure_rate_percent > 10 ? 'var(--rose-danger)' : 'var(--emerald-safe)' }}>
              {metrics.failure_rate_percent}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Analysis error threshold</div>
          </div>

          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Average Latency</div>
            <div style={{ fontSize: '1.85rem', fontWeight: 800, fontFamily: 'var(--font-mono)', marginTop: '0.25rem' }}>
              {metrics.avg_processing_time_sec}s
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Inference & feature extraction</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid var(--border-color)', marginBottom: '1.5rem' }}>
        {[
          { key: 'users', label: 'User & Role Access Control', icon: Users },
          { key: 'models', label: 'Registered Model Architectures', icon: Cpu },
          { key: 'audit', label: 'Immutable System Audit Logs', icon: ShieldAlert },
        ].map(t => {
          const active = activeTab === t.key;
          const Icon = t.icon;
          return (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.25rem',
                border: 'none',
                background: 'none',
                color: active ? 'var(--cyan-primary)' : 'var(--text-muted)',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: 'pointer',
                borderBottom: active ? '2px solid var(--cyan-primary)' : '2px solid transparent',
                transition: 'var(--transition-fast)'
              }}
            >
              <Icon size={16} />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab 1: User Management */}
      {activeTab === 'users' && (
        <div className="card">
          <h3 style={{ fontSize: '1.15rem', marginBottom: '0.25rem' }}>Registered Accounts & Role RBAC</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
            Assign elevated review permissions or administrative rights to trusted forensic personnel.
          </p>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Full Name</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Email Address</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Registered Date</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Current Role</th>
                  <th style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>Assign New Role</th>
                </tr>
              </thead>
              <tbody>
                {usersList.map((u) => (
                  <tr key={u.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '0.875rem 0.5rem', fontWeight: 600 }}>{u.full_name}</td>
                    <td style={{ padding: '0.875rem 0.5rem', color: 'var(--text-secondary)' }}>{u.email}</td>
                    <td style={{ padding: '0.875rem 0.5rem', color: 'var(--text-muted)', fontSize: '0.775rem' }}>
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem' }}>
                      <span className={`badge ${u.role === 'admin' ? 'badge-manipulated' : (u.role === 'reviewer' ? 'badge-cyan' : 'badge-pending')}`}>
                        {u.role.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: '0.875rem 0.5rem', textAlign: 'right' }}>
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        className="select-control"
                        style={{ width: 'auto', padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                      >
                        <option value="user">User (Analyst)</option>
                        <option value="reviewer">Reviewer</option>
                        <option value="admin">Administrator</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Models & Registry */}
      {activeTab === 'models' && (
        <div className="card">
          <h3 style={{ fontSize: '1.15rem', marginBottom: '0.25rem' }}>Active AI Model Architectures</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
            Registered inference backbones, feature extractors, and benchmark data sources.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {modelsList.map((m, idx) => (
              <div key={idx} style={{
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                padding: '1.25rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span className="badge badge-cyan">{m.media_type.toUpperCase()}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>v{m.version}</span>
                </div>
                <h4 style={{ fontSize: '1.1rem', marginBottom: '0.35rem' }}>{m.name}</h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.875rem' }}>{m.architecture}</p>

                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                  <strong>Trained On:</strong> {m.trained_on || 'FaceForensics++'}
                </div>

                {m.metrics && (
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: '0.5rem',
                    padding: '0.75rem',
                    background: 'rgba(255, 255, 255, 0.02)',
                    borderRadius: 'var(--radius-sm)',
                    textAlign: 'center',
                    fontSize: '0.75rem'
                  }}>
                    <div>
                      <div style={{ color: 'var(--text-muted)' }}>Accuracy</div>
                      <div style={{ fontWeight: 700, color: 'var(--emerald-safe)' }}>{(m.metrics.accuracy * 100).toFixed(1)}%</div>
                    </div>
                    <div>
                      <div style={{ color: 'var(--text-muted)' }}>F1-Score</div>
                      <div style={{ fontWeight: 700, color: '#38bdf8' }}>{(m.metrics.f1_score * 100).toFixed(1)}%</div>
                    </div>
                    <div>
                      <div style={{ color: 'var(--text-muted)' }}>Latency</div>
                      <div style={{ fontWeight: 700 }}>{m.metrics.latency_ms}ms</div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Immutable Audit Logs */}
      {activeTab === 'audit' && (
        <div className="card">
          <h3 style={{ fontSize: '1.15rem', marginBottom: '0.25rem' }}>Security & Operation Audit Logs</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
            Cryptographically timestamped actions, logins, status alterations, and uploads.
          </p>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '0.65rem 0.5rem' }}>Timestamp</th>
                  <th style={{ padding: '0.65rem 0.5rem' }}>Action</th>
                  <th style={{ padding: '0.65rem 0.5rem' }}>User Email</th>
                  <th style={{ padding: '0.65rem 0.5rem' }}>Target Resource</th>
                  <th style={{ padding: '0.65rem 0.5rem' }}>Audit Details</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '0.75rem 0.5rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600 }}>
                      <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>{log.action}</span>
                    </td>
                    <td style={{ padding: '0.75rem 0.5rem', color: 'var(--text-secondary)' }}>
                      {log.user_email || 'System'}
                    </td>
                    <td style={{ padding: '0.75rem 0.5rem', color: 'var(--text-muted)' }}>
                      {log.resource_type}: {log.resource_id ? log.resource_id.slice(0, 10) : 'N/A'}
                    </td>
                    <td style={{ padding: '0.75rem 0.5rem', color: 'var(--text-secondary)' }}>
                      {typeof log.details === 'object' ? JSON.stringify(log.details) : log.details || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
