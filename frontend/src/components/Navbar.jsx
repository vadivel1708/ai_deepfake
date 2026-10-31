import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, 
  Cpu, 
  UploadCloud, 
  LayoutDashboard, 
  History, 
  FileText, 
  Sliders, 
  LogOut, 
  Menu, 
  X,
  UserCheck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, isReviewer, isAdmin, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, authRequired: true },
    { label: 'Analyze Media', path: '/analyze', icon: UploadCloud, authRequired: true },
    { label: 'Review Queue', path: '/reviews', icon: UserCheck, reviewerOnly: true },
    { label: 'History', path: '/history', icon: History, authRequired: true },
    { label: 'Reports', path: '/reports', icon: FileText, authRequired: true },
    { label: 'Admin', path: '/admin', icon: Sliders, adminOnly: true },
  ];

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      background: 'rgba(7, 10, 18, 0.85)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-color)',
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '0 1.5rem',
        height: '4.25rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Brand Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', textDecoration: 'none' }}>
          <div style={{
            width: '2.5rem',
            height: '2.5rem',
            borderRadius: 'var(--radius-sm)',
            background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(6, 182, 212, 0.4)'
          }}>
            <ShieldCheck size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontWeight: 800, fontSize: '1.15rem', letterSpacing: '-0.02em', color: '#ffffff' }}>
                DEEP<span style={{ color: 'var(--cyan-primary)' }}>SHIELD</span>
              </span>
              <span style={{
                fontSize: '0.625rem',
                padding: '0.125rem 0.375rem',
                background: 'rgba(6, 182, 212, 0.15)',
                border: '1px solid rgba(6, 182, 212, 0.3)',
                borderRadius: '4px',
                color: '#38bdf8',
                fontWeight: 700,
                letterSpacing: '0.05em'
              }}>
                FORENSIC AI
              </span>
            </div>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: 1 }}>
              Media Authenticity Analysis
            </p>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <nav style={{ display: 'none', alignItems: 'center', gap: '0.375rem' }} className="desktop-nav">
          {navItems.map((item) => {
            if (item.authRequired && !isAuthenticated) return null;
            if (item.reviewerOnly && !isReviewer) return null;
            if (item.adminOnly && !isAdmin) return null;

            const active = location.pathname === item.path;
            const Icon = item.icon;

            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 0.875rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  textDecoration: 'none',
                  color: active ? '#ffffff' : 'var(--text-secondary)',
                  background: active ? 'rgba(6, 182, 212, 0.12)' : 'transparent',
                  border: active ? '1px solid rgba(6, 182, 212, 0.3)' : '1px solid transparent',
                  transition: 'var(--transition-fast)'
                }}
              >
                <Icon size={16} color={active ? 'var(--cyan-primary)' : 'currentColor'} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* User Account / Auth Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
          {isAuthenticated ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.625rem',
                padding: '0.375rem 0.75rem',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-full)',
              }}>
                <div style={{
                  width: '1.75rem',
                  height: '1.75rem',
                  borderRadius: '50%',
                  background: user.role === 'admin' ? '#ef4444' : (user.role === 'reviewer' ? '#3b82f6' : '#10b981'),
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 700
                }}>
                  {user.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, lineHeight: 1.2 }}>{user.full_name}</div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    {user.role}
                  </div>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="btn btn-secondary"
                title="Log Out"
                style={{ padding: '0.5rem', borderRadius: 'var(--radius-sm)' }}
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <Link to="/login" className="btn btn-secondary">Sign In</Link>
              <Link to="/register" className="btn btn-primary">Register</Link>
            </div>
          )}

          {/* Mobile hamburger toggle */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              display: 'block'
            }}
            className="mobile-toggle"
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileOpen && (
        <div style={{
          background: 'rgba(10, 15, 28, 0.98)',
          borderBottom: '1px solid var(--border-color)',
          padding: '1rem 1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
          {navItems.map((item) => {
            if (item.authRequired && !isAuthenticated) return null;
            if (item.reviewerOnly && !isReviewer) return null;
            if (item.adminOnly && !isAdmin) return null;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.75rem',
                  color: 'var(--text-primary)',
                  textDecoration: 'none',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem'
                }}
              >
                <item.icon size={18} color="var(--cyan-primary)" />
                {item.label}
              </Link>
            );
          })}
        </div>
      )}

      <style>{`
        @media (min-width: 768px) {
          .desktop-nav { display: flex !important; }
          .mobile-toggle { display: none !important; }
        }
      `}</style>
    </header>
  );
}
