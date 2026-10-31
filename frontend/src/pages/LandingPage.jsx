import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  Cpu, 
  Eye, 
  FileCheck2, 
  Activity, 
  Layers, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight,
  Video,
  Image as ImageIcon,
  Mic,
  Lock
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LandingPage() {
  const { isAuthenticated } = useAuth();

  const features = [
    {
      icon: ImageIcon,
      title: 'Image Authenticity & ELA',
      desc: 'Error Level Analysis (ELA) and 2D-FFT frequency spectrum decomposition detect localized tampering, generative GAN textures, and diffusion model artifacts.',
      tag: 'Spatial & Frequency Domain'
    },
    {
      icon: Video,
      title: 'Video Face Tracking & Temporal Aggregation',
      desc: 'Frame-by-frame Haar/DNN face extraction with temporal consistency metrics. Detects inter-frame facial jitter, eye-blink inconsistencies, and blending seams.',
      tag: 'Temporal Coherence'
    },
    {
      icon: Mic,
      title: 'Synthetic Speech & Audio Vocoder Analysis',
      desc: 'Short-Time Fourier Transform (STFT) Wiener entropy and spectral flatness inspection uncovers neural vocoder synthesis (WaveNet, HiFi-GAN) and voice clones.',
      tag: 'Acoustic Forensics'
    },
    {
      icon: FileCheck2,
      title: 'Human-in-the-Loop & Audit Reports',
      desc: 'Independent human reviewer workflow separates model probabilities from final ground truth. Generates tamper-evident downloadable PDF and CSV forensic reports.',
      tag: 'Defense-Grade Verification'
    }
  ];

  const workflowSteps = [
    {
      step: '01',
      title: 'Secure Ingestion & Validation',
      desc: 'Client-validated media upload with strict MIME type checking, size enforcement, and SHA-256 cryptographic hashing to establish chain of custody.'
    },
    {
      step: '02',
      title: 'Multi-Modal Forensic Pipeline',
      desc: 'Media is decoded safely in isolation. The system generates ELA error maps, 2D-FFT power spectrums, sampled video face crops, or acoustic spectral flatness.'
    },
    {
      step: '03',
      title: 'Neural Inference & Calibration',
      desc: 'MesoInception neural backbones and spectral feature classifiers evaluate artifacts, outputting calibrated manipulation probabilities and uncertainty bounds.'
    },
    {
      step: '04',
      title: 'Forensic Review & Verifiable Report',
      desc: 'Reviewers inspect suspicious frames, ELA diffs, and acoustic anomalies, submit authorized verdicts, and export signed verification PDF dossiers.'
    }
  ];

  return (
    <div style={{ paddingBottom: '5rem' }}>
      {/* Hero Section */}
      <section style={{
        position: 'relative',
        padding: '5rem 1.5rem 4rem',
        maxWidth: '1280px',
        margin: '0 auto',
        textAlign: 'center'
      }}>
        {/* Glowing badge */}
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.35rem 1rem',
          background: 'rgba(6, 182, 212, 0.1)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          borderRadius: 'var(--radius-full)',
          fontSize: '0.8rem',
          fontWeight: 600,
          color: 'var(--cyan-glow)',
          marginBottom: '1.75rem',
          boxShadow: 'var(--border-glow)'
        }}>
          <Sparkles size={14} />
          <span>Next-Generation AI Media Authenticity & Deepfake Forensic System</span>
        </div>

        <h1 style={{
          fontSize: 'clamp(2.2rem, 5vw, 3.75rem)',
          lineHeight: 1.15,
          fontWeight: 800,
          maxWidth: '960px',
          margin: '0 auto 1.5rem'
        }}>
          Detect Synthetic Media, AI Face-Swaps, and Voice Clones with <span className="gradient-text">Forensic Precision</span>
        </h1>

        <p style={{
          fontSize: 'clamp(1rem, 2vw, 1.2rem)',
          color: 'var(--text-secondary)',
          maxWidth: '740px',
          margin: '0 auto 2.5rem',
          lineHeight: 1.6
        }}>
          A multi-modal authenticity analysis platform integrating Error Level Analysis (ELA), 2D-FFT spectral decomposition, OpenCV temporal video face-tracking, and synthetic speech vocoder detection.
        </p>

        {/* CTA Buttons */}
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '1rem' }}>
          <Link
            to={isAuthenticated ? "/analyze" : "/register"}
            className="btn btn-primary"
            style={{ fontSize: '1rem', padding: '0.875rem 2rem' }}
          >
            <ShieldCheck size={20} />
            Launch Forensic Analysis
            <ArrowRight size={18} />
          </Link>
          <Link
            to={isAuthenticated ? "/dashboard" : "/login"}
            className="btn btn-secondary"
            style={{ fontSize: '1rem', padding: '0.875rem 2rem' }}
          >
            Explore Dashboard & Demos
          </Link>
        </div>

        {/* Quick Highlights Banner */}
        <div style={{
          marginTop: '4rem',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1.25rem',
          textAlign: 'left'
        }}>
          <div className="card">
            <div style={{ color: 'var(--cyan-primary)', fontSize: '1.75rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>91.2%</div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginTop: '0.25rem' }}>Image Model Accuracy</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Evaluated on FaceForensics++ (c23)</div>
          </div>
          <div className="card">
            <div style={{ color: '#38bdf8', fontSize: '1.75rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>0.954</div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginTop: '0.25rem' }}>ROC-AUC Metric</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>High discrimination benchmark</div>
          </div>
          <div className="card">
            <div style={{ color: 'var(--emerald-safe)', fontSize: '1.75rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>3 Modalities</div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginTop: '0.25rem' }}>Images, Videos & Audio</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Full multi-modal coverage</div>
          </div>
          <div className="card">
            <div style={{ color: '#a855f7', fontSize: '1.75rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>Zero-Trust</div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginTop: '0.25rem' }}>Human Review Separation</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>AI outputs distinct from final verdict</div>
          </div>
        </div>
      </section>

      {/* Forensic Capabilities Grid */}
      <section style={{ maxWidth: '1280px', margin: '4rem auto', padding: '0 1.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Comprehensive Forensic Indicators</h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
            Traditional deepfake detectors rely only on black-box predictions. DeepShield combines deep neural models with explainable signal-processing indicators.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.5rem'
        }}>
          {features.map((f, i) => (
            <div key={i} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{
                width: '3rem',
                height: '3rem',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(6, 182, 212, 0.1)',
                border: '1px solid rgba(6, 182, 212, 0.25)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1.25rem'
              }}>
                <f.icon size={24} color="var(--cyan-primary)" />
              </div>
              <span className="badge badge-cyan" style={{ alignSelf: 'flex-start', marginBottom: '0.75rem' }}>
                {f.tag}
              </span>
              <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>{f.title}</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6, flexGrow: 1 }}>
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Forensic Architecture & Workflow */}
      <section style={{
        maxWidth: '1280px',
        margin: '5rem auto',
        padding: '0 1.5rem'
      }}>
        <div className="glass-panel" style={{ padding: '3rem 2rem' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <span className="badge badge-cyan" style={{ marginBottom: '0.5rem' }}>PIPELINE WORKFLOW</span>
            <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>How DeepShield Analyzes Media</h2>
            <p style={{ color: 'var(--text-secondary)', maxWidth: '650px', margin: '0 auto' }}>
              From initial ingestion to verifiable human review, each phase is logged and cryptographically audited.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '1.5rem'
          }}>
            {workflowSteps.map((step, idx) => (
              <div key={idx} style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '1.5rem',
                position: 'relative'
              }}>
                <div style={{
                  fontSize: '2.5rem',
                  fontWeight: 800,
                  color: 'rgba(6, 182, 212, 0.2)',
                  fontFamily: 'var(--font-mono)',
                  marginBottom: '0.5rem'
                }}>
                  {step.step}
                </div>
                <h4 style={{ fontSize: '1.05rem', marginBottom: '0.5rem' }}>{step.title}</h4>
                <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Ready to Analyze CTA */}
      <section style={{
        maxWidth: '800px',
        margin: '4rem auto 0',
        padding: '0 1.5rem',
        textAlign: 'center'
      }}>
        <div className="card" style={{
          padding: '3rem 2rem',
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)',
          border: '1px solid rgba(6, 182, 212, 0.3)'
        }}>
          <h2 style={{ fontSize: '1.85rem', marginBottom: '0.75rem' }}>Ready to Investigate Media Authenticity?</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.75rem', fontSize: '0.95rem' }}>
            Sign in with demo credentials or upload an image, video, or audio file to inspect frame-by-frame forensics now.
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <Link to="/analyze" className="btn btn-primary" style={{ padding: '0.75rem 2rem' }}>
              Start Analysis Now
            </Link>
            <Link to="/login" className="btn btn-secondary" style={{ padding: '0.75rem 1.5rem' }}>
              Sign In to Dashboard
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
