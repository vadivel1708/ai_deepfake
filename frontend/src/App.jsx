import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import MediaAnalysis from './pages/MediaAnalysis';
import ForensicEvidenceViewer from './pages/ForensicEvidenceViewer';
import AnalysisHistory from './pages/AnalysisHistory';
import ReviewQueue from './pages/ReviewQueue';
import ReportsOverview from './pages/ReportsOverview';
import AdminDashboard from './pages/AdminDashboard';

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Navbar />
          <main style={{ flexGrow: 1 }}>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected User Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/analyze"
                element={
                  <ProtectedRoute>
                    <MediaAnalysis />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/analysis/:id"
                element={
                  <ProtectedRoute>
                    <ForensicEvidenceViewer />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/history"
                element={
                  <ProtectedRoute>
                    <AnalysisHistory />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/reports"
                element={
                  <ProtectedRoute>
                    <ReportsOverview />
                  </ProtectedRoute>
                }
              />

              {/* Reviewer Protected Route */}
              <Route
                path="/reviews"
                element={
                  <ProtectedRoute roleRequired="reviewer">
                    <ReviewQueue />
                  </ProtectedRoute>
                }
              />

              {/* Administrator Protected Route */}
              <Route
                path="/admin"
                element={
                  <ProtectedRoute roleRequired="admin">
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />

              {/* Catch-all redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}
