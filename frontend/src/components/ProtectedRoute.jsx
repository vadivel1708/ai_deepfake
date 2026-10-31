import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ children, roleRequired }) {
  const { user, isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '60vh',
        color: 'var(--cyan-primary)'
      }}>
        <div className="animate-spin" style={{
          width: '2.5rem',
          height: '2.5rem',
          border: '3px solid rgba(6, 182, 212, 0.2)',
          borderTopColor: 'var(--cyan-primary)',
          borderRadius: '50%'
        }} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (roleRequired) {
    if (roleRequired === 'reviewer' && user?.role !== 'reviewer' && user?.role !== 'admin') {
      return <Navigate to="/dashboard" replace />;
    }
    if (roleRequired === 'admin' && user?.role !== 'admin') {
      return <Navigate to="/dashboard" replace />;
    }
  }

  return children;
}
