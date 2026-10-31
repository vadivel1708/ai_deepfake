import React from 'react';
import { ShieldCheck, AlertTriangle } from 'lucide-react';

export default function Footer() {
  return (
    <footer style={{
      borderTop: '1px solid var(--border-color)',
      background: 'rgba(7, 10, 18, 0.95)',
      marginTop: 'auto',
      padding: '2.5rem 1.5rem',
      color: 'var(--text-secondary)',
      fontSize: '0.85rem'
    }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <ShieldCheck size={20} color="var(--cyan-primary)" />
            <span style={{ fontWeight: 700, color: '#ffffff' }}>DEEPSHIELD AI</span>
            <span style={{ color: 'var(--text-muted)' }}>| Media Authenticity & Deepfake Forensic Analysis</span>
          </div>
          <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8rem' }}>
            <span>Architecture: MesoInception + 2D-FFT + Audio Vocoder</span>
            <span>Version 1.2.0</span>
          </div>
        </div>

        <div style={{
          padding: '0.875rem 1rem',
          background: 'rgba(244, 63, 94, 0.06)',
          border: '1px solid rgba(244, 63, 94, 0.2)',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.75rem',
          fontSize: '0.775rem',
          color: '#cbd5e1'
        }}>
          <AlertTriangle size={18} color="#fb7185" style={{ flexShrink: 0, marginTop: '2px' }} />
          <span>
            <strong>Legal & Forensic Disclaimer:</strong> AI model predictions, uncertainty scores, and forensic heatmaps reflect probabilistic algorithmic metrics. They do not constitute legally conclusive proof of media manipulation or absolute authenticity. Final verification must always be performed by a qualified human forensic analyst.
          </span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
          <span>© 2026 DeepShield Forensic Lab. All rights reserved.</span>
          <span>College Final-Year AI/ML Capstone Project & Technical Demonstration</span>
        </div>
      </div>
    </footer>
  );
}
