import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  AlertTriangle, 
  FileCheck, 
  HelpCircle, 
  Download, 
  RefreshCw, 
  ArrowLeft, 
  Clock, 
  Cpu, 
  Eye, 
  UserCheck, 
  CheckCircle2, 
  Image as ImageIcon, 
  Video, 
  Mic, 
  FileText
} from 'lucide-react';
import { Line } from 'react-chartjs-2';
import { analysisAPI, reviewAPI, reportAPI, STORAGE_BASE_URL } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function ForensicEvidenceViewer() {
  const { id } = useParams();
  const { isReviewer, user } = useAuth();

  const [loading, setLoading] = useState(true);
  const [job, setJob] = useState(null);
  const [error, setError] = useState('');
  const [activeImageTab, setActiveImageTab] = useState('original'); // 'original', 'ela', 'fft'

  // Reviewer state
  const [reviewStatus, setReviewStatus] = useState('pending_review');
  const [reviewNotes, setReviewNotes] = useState('');
  const [updatingReview, setUpdatingReview] = useState(false);
  const [reviewSuccess, setReviewSuccess] = useState('');

  const fetchJobData = async () => {
    setLoading(true);
    try {
      const res = await analysisAPI.getJob(id);
      setJob(res.data);
      if (res.data.review_status) setReviewStatus(res.data.review_status);
      if (res.data.review_notes) setReviewNotes(res.data.review_notes);
    } catch (err) {
      setError('Could not load analysis record. ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobData();
  }, [id]);

  const handleUpdateReviewStatus = async () => {
    setUpdatingReview(true);
    setReviewSuccess('');
    try {
      await reviewAPI.updateStatus(id, reviewStatus, reviewNotes);
      setReviewSuccess('Review verdict and notes updated successfully.');
      fetchJobData();
    } catch (err) {
      setError('Failed to update review status: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUpdatingReview(false);
    }
  };

  const handleRetry = async () => {
    try {
      await analysisAPI.retry(id);
      fetchJobData();
    } catch (err) {
      setError('Retry failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: '1rem' }}>
        <div className="animate-spin" style={{ width: '3rem', height: '3rem', border: '3px solid rgba(6, 182, 212, 0.2)', borderTopColor: 'var(--cyan-primary)', borderRadius: '50%' }} />
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Loading forensic evidence file...</p>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div style={{ maxWidth: '600px', margin: '4rem auto', padding: '2rem', textAlign: 'center' }} className="card">
        <AlertTriangle size={36} color="var(--rose-danger)" style={{ margin: '0 auto 1rem' }} />
        <h3>Unable to Load Forensic Report</h3>
        <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem', marginBottom: '1.5rem' }}>{error}</p>
        <Link to="/dashboard" className="btn btn-primary">Return to Dashboard</Link>
      </div>
    );
  }

  // Prediction styling
  const isAuthentic = job.prediction === 'likely_authentic';
  const isManipulated = job.prediction === 'potentially_manipulated';
  const isInconclusive = job.prediction === 'inconclusive';

  let bannerClass = 'badge-inconclusive';
  let bannerBg = 'rgba(245, 158, 11, 0.1)';
  let bannerBorder = 'rgba(245, 158, 11, 0.3)';
  let bannerText = '#fbbf24';
  let BannerIcon = HelpCircle;

  if (isAuthentic) {
    bannerClass = 'badge-authentic';
    bannerBg = 'rgba(16, 185, 129, 0.1)';
    bannerBorder = 'rgba(16, 185, 129, 0.3)';
    bannerText = '#34d399';
    BannerIcon = FileCheck;
  } else if (isManipulated) {
    bannerClass = 'badge-manipulated';
    bannerBg = 'rgba(244, 63, 94, 0.1)';
    bannerBorder = 'rgba(244, 63, 94, 0.3)';
    bannerText = '#fb7185';
    BannerIcon = AlertTriangle;
  }

  // Chart data for video frame timeline
  const frameScores = job.frame_predictions || [];
  const timelineData = {
    labels: frameScores.map(f => `${f.timestamp_seconds}s`),
    datasets: [
      {
        label: 'Frame Manipulation Score',
        data: frameScores.map(f => f.score),
        borderColor: '#06b6d4',
        backgroundColor: 'rgba(6, 182, 212, 0.15)',
        fill: true,
        tension: 0.3,
        pointBackgroundColor: frameScores.map(f => f.is_suspicious ? '#f43f5e' : '#10b981'),
        pointRadius: 4,
      },
      {
        label: 'Suspicion Threshold (0.60)',
        data: frameScores.map(() => 0.60),
        borderColor: 'rgba(244, 63, 94, 0.5)',
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false,
      }
    ]
  };

  const timelineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } } },
      tooltip: {
        callbacks: {
          afterLabel: (ctx) => {
            const idx = ctx.dataIndex;
            const fp = frameScores[idx];
            return fp?.face_detected ? 'Face Detected: Yes' : 'Face Detected: No';
          }
        }
      }
    },
    scales: {
      x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
      y: { min: 0, max: 1, ticks: { color: '#64748b' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
    }
  };

  const indicators = job.forensic_indicators || {};

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem 1.5rem 5rem' }}>
      {/* Navigation & Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <Link to="/dashboard" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', textDecoration: 'none', fontSize: '0.875rem' }}>
          <ArrowLeft size={16} />
          Back to Dashboard
        </Link>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <a
            href={reportAPI.downloadPdfUrl(job.id)}
            target="_blank"
            rel="noreferrer"
            className="btn btn-primary"
            style={{ fontSize: '0.825rem' }}
          >
            <Download size={15} />
            Download PDF Dossier
          </a>
          <a
            href={reportAPI.downloadCsvUrl(job.id)}
            target="_blank"
            rel="noreferrer"
            className="btn btn-secondary"
            style={{ fontSize: '0.825rem' }}
          >
            <FileText size={15} />
            Export CSV
          </a>
          {job.status === 'failed' && (
            <button onClick={handleRetry} className="btn btn-secondary" style={{ fontSize: '0.825rem' }}>
              <RefreshCw size={15} />
              Retry Job
            </button>
          )}
        </div>
      </div>

      {/* Case Header Details */}
      <div className="glass-panel" style={{ padding: '1.5rem 2rem', marginBottom: '1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span className="badge badge-cyan">{job.media_type || 'MEDIA'}</span>
              <h2 style={{ fontSize: '1.4rem' }}>{job.original_filename || 'Media Item'}</h2>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: '0.25rem' }}>
              Analysis ID: {job.id} | Processed: {new Date(job.created_at).toLocaleString()}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <div>
              <div style={{ color: 'var(--text-muted)' }}>Model Architecture</div>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{job.model_name || 'MesoInception-ForensicEnsemble'}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)' }}>Version</div>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>v{job.model_version || '1.2.0'}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)' }}>Latency</div>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{job.processing_time_seconds || 0}s</div>
            </div>
          </div>
        </div>
      </div>

      {/* High-Impact AI Prediction Banner */}
      <div style={{
        padding: '1.75rem 2rem',
        background: bannerBg,
        border: `1px solid ${bannerBorder}`,
        borderRadius: 'var(--radius-md)',
        marginBottom: '2rem',
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '1.5rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{
            width: '3.5rem',
            height: '3.5rem',
            borderRadius: 'var(--radius-sm)',
            background: bannerBorder,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
          }}>
            <BannerIcon size={32} color={bannerText} />
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              PROBABILISTIC AI INFERENCE VERDICT
            </span>
            <h2 style={{ fontSize: '1.75rem', color: bannerText, lineHeight: 1.2 }}>
              {(job.prediction || 'INCONCLUSIVE').replace('_', ' ').toUpperCase()}
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '0.25rem' }}>
              {job.recommendations || 'Standard forensic protocol recommended.'}
            </p>
          </div>
        </div>

        {/* Confidence Probability Gauge */}
        <div style={{ minWidth: '240px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>Manipulation Likelihood:</span>
            <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: bannerText }}>
              {job.confidence_score !== null ? `${(job.confidence_score * 100).toFixed(1)}%` : 'N/A'}
            </span>
          </div>
          <div style={{ width: '100%', height: '10px', background: 'rgba(0, 0, 0, 0.4)', borderRadius: '5px', overflow: 'hidden' }}>
            <div style={{
              width: `${(job.confidence_score || 0) * 100}%`,
              height: '100%',
              background: bannerText,
              transition: 'width 0.5s ease'
            }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            <span>Uncertainty: {job.uncertainty_score !== null ? `${(job.uncertainty_score * 100).toFixed(1)}%` : 'N/A'}</span>
            <span>Threshold: 58.0%</span>
          </div>
        </div>
      </div>

      {/* Warnings & Notices */}
      {job.warnings && job.warnings.length > 0 && (
        <div style={{
          padding: '1rem 1.25rem',
          background: 'rgba(245, 158, 11, 0.08)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '2rem',
          fontSize: '0.825rem',
          color: '#fef3c7'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#fbbf24', marginBottom: '0.35rem' }}>
            <AlertTriangle size={16} />
            Analysis Quality Warnings
          </div>
          <ul style={{ paddingLeft: '1.25rem', margin: 0 }}>
            {job.warnings.map((w, idx) => (
              <li key={idx}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Modality-Specific Evidence Section */}
      <div style={{ marginBottom: '2.5rem' }}>
        {job.media_type === 'image' && (
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem' }}>Visual Forensic Indicator Inspection</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Examine Error Level Analysis (ELA) compression differences and 2D-FFT high-frequency power spectrums.
                </p>
              </div>

              {/* View Switcher Tabs */}
              <div style={{ display: 'flex', background: 'rgba(0, 0, 0, 0.3)', borderRadius: 'var(--radius-sm)', padding: '0.25rem' }}>
                <button
                  onClick={() => setActiveImageTab('original')}
                  className="btn"
                  style={{
                    padding: '0.4rem 0.85rem',
                    fontSize: '0.8rem',
                    background: activeImageTab === 'original' ? 'var(--cyan-primary)' : 'transparent',
                    color: activeImageTab === 'original' ? '#fff' : 'var(--text-secondary)'
                  }}
                >
                  Original Source
                </button>
                <button
                  onClick={() => setActiveImageTab('ela')}
                  className="btn"
                  style={{
                    padding: '0.4rem 0.85rem',
                    fontSize: '0.8rem',
                    background: activeImageTab === 'ela' ? 'var(--cyan-primary)' : 'transparent',
                    color: activeImageTab === 'ela' ? '#fff' : 'var(--text-secondary)'
                  }}
                >
                  ELA Compression Diff
                </button>
                <button
                  onClick={() => setActiveImageTab('fft')}
                  className="btn"
                  style={{
                    padding: '0.4rem 0.85rem',
                    fontSize: '0.8rem',
                    background: activeImageTab === 'fft' ? 'var(--cyan-primary)' : 'transparent',
                    color: activeImageTab === 'fft' ? '#fff' : 'var(--text-secondary)'
                  }}
                >
                  2D-FFT Spectrum
                </button>
              </div>
            </div>

            {/* Image Preview Canvas */}
            <div style={{
              background: '#04070e',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              padding: '1.5rem',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '400px'
            }}>
              {activeImageTab === 'original' && (
                <div style={{ textAlign: 'center' }}>
                  <img
                    src={`${STORAGE_BASE_URL}/storage/uploads/${job.original_filename || ''}`}
                    alt="Original Upload"
                    onError={(e) => {
                      // Fallback preview
                      e.target.style.display = 'none';
                    }}
                    style={{ maxHeight: '480px', maxWidth: '100%', borderRadius: '4px', objectFit: 'contain' }}
                  />
                  <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Original uploaded bitmap. Notice facial region boundaries and lighting coherence.
                  </p>
                </div>
              )}

              {activeImageTab === 'ela' && (
                <div style={{ textAlign: 'center' }}>
                  {indicators.ela?.preview_url ? (
                    <img
                      src={`${STORAGE_BASE_URL}${indicators.ela.preview_url}`}
                      alt="Error Level Analysis"
                      style={{ maxHeight: '480px', maxWidth: '100%', borderRadius: '4px' }}
                    />
                  ) : (
                    <div style={{ color: 'var(--text-muted)' }}>ELA visualization is being processed or unavailable.</div>
                  )}
                  <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: '600px' }}>
                    <strong>Error Level Analysis (ELA):</strong> Highlighted white/bright pixels indicate areas with significantly different JPEG recompression rates, typically matching spliced or neural-synthesized face crops.
                  </p>
                </div>
              )}

              {activeImageTab === 'fft' && (
                <div style={{ textAlign: 'center' }}>
                  {indicators.frequency_analysis?.preview_url ? (
                    <img
                      src={`${STORAGE_BASE_URL}${indicators.frequency_analysis.preview_url}`}
                      alt="2D-FFT Magnitude Spectrum"
                      style={{ maxHeight: '480px', maxWidth: '100%', borderRadius: '4px' }}
                    />
                  ) : (
                    <div style={{ color: 'var(--text-muted)' }}>FFT visualization is being processed or unavailable.</div>
                  )}
                  <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: '600px' }}>
                    <strong>2D Fast Fourier Transform (FFT):</strong> Generative models (StyleGAN, Diffusion) produce distinctive star-burst or periodic spikes in high-frequency spectral bands that deviate from natural 1/f camera noise.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {job.media_type === 'video' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {/* Frame Score Timeline */}
            <div className="card">
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>Frame-by-Frame Manipulation Timeline</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                Temporal scores mapped across sampled frames. Spikes indicate abrupt face swaps or blending glitches.
              </p>
              <div style={{ height: '280px', position: 'relative' }}>
                <Line data={timelineData} options={timelineOptions} />
              </div>
            </div>

            {/* Suspicious Frames Carousel / Gallery */}
            <div className="card">
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>Sampled Frame Gallery & Face Tracking</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                Red bounding boxes indicate frames exceeding the suspicion threshold (Score &ge; 0.60).
              </p>

              {frameScores.length === 0 ? (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No individual frame crops available.</p>
              ) : (
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                  gap: '1rem'
                }}>
                  {frameScores.map((frame, idx) => (
                    <div
                      key={frame.id || idx}
                      style={{
                        background: 'rgba(0, 0, 0, 0.4)',
                        border: `1px solid ${frame.is_suspicious ? 'rgba(244, 63, 94, 0.4)' : 'rgba(255, 255, 255, 0.08)'}`,
                        borderRadius: 'var(--radius-sm)',
                        overflow: 'hidden'
                      }}
                    >
                      {frame.thumbnail_url ? (
                        <img
                          src={`${STORAGE_BASE_URL}${frame.thumbnail_url}`}
                          alt={`Frame ${frame.frame_index}`}
                          style={{ width: '100%', height: '120px', objectFit: 'cover' }}
                        />
                      ) : (
                        <div style={{ height: '120px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                          Frame #{frame.frame_index}
                        </div>
                      )}
                      <div style={{ padding: '0.625rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.25rem' }}>
                          <span style={{ color: 'var(--text-muted)' }}>Time: {frame.timestamp_seconds}s</span>
                          <span style={{
                            fontWeight: 700,
                            fontFamily: 'var(--font-mono)',
                            color: frame.is_suspicious ? 'var(--rose-danger)' : 'var(--emerald-safe)'
                          }}>
                            {(frame.score * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          {frame.face_detected ? 'Face Detected' : 'Global Frame'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {job.media_type === 'audio' && (
          <div className="card">
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>Acoustic Vocoder & Synthetic Speech Diagnostics</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
              Evaluation of STFT Wiener spectral entropy, robotic pitch stability, and neural vocoder artifacts.
            </p>

            {/* Audio Segments Breakdown */}
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                    <th style={{ padding: '0.5rem' }}>Segment</th>
                    <th style={{ padding: '0.5rem' }}>Time Range</th>
                    <th style={{ padding: '0.5rem' }}>Spectral Flatness (Entropy)</th>
                    <th style={{ padding: '0.5rem' }}>HF Vocoder Anomaly</th>
                    <th style={{ padding: '0.5rem' }}>Segment Score</th>
                    <th style={{ padding: '0.5rem' }}>Verdict</th>
                  </tr>
                </thead>
                <tbody>
                  {(job.audio_segments || []).map((seg, idx) => (
                    <tr key={seg.id || idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                      <td style={{ padding: '0.75rem 0.5rem' }}>#{seg.segment_index + 1}</td>
                      <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'var(--font-mono)' }}>
                        {seg.start_time_seconds}s - {seg.end_time_seconds}s
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'var(--font-mono)' }}>
                        {seg.spectral_flatness !== null ? seg.spectral_flatness : 'N/A'}
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'var(--font-mono)' }}>
                        {seg.mfcc_anomaly_score !== null ? seg.mfcc_anomaly_score : 'N/A'}
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                        {(seg.score * 100).toFixed(1)}%
                      </td>
                      <td style={{ padding: '0.75rem 0.5rem' }}>
                        <span className={`badge ${seg.is_suspicious ? 'badge-manipulated' : 'badge-authentic'}`}>
                          {seg.is_suspicious ? 'SUSPICIOUS' : 'NORMAL'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Human Forensic Review Action Panel */}
      <div className="card" style={{
        padding: '2rem',
        border: '1px solid rgba(6, 182, 212, 0.3)',
        background: 'linear-gradient(135deg, rgba(16, 24, 44, 0.85) 0%, rgba(14, 21, 38, 0.95) 100%)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <UserCheck size={24} color="var(--cyan-primary)" />
          <div>
            <h3 style={{ fontSize: '1.25rem' }}>Human Forensic Review Determination</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Independent human-in-the-loop verification protocol. Changes are cryptographically logged to the audit registry.
            </p>
          </div>
        </div>

        {reviewSuccess && (
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
            marginBottom: '1.25rem'
          }}>
            <CheckCircle2 size={16} />
            <span>{reviewSuccess}</span>
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Final Reviewer Classification
            </label>
            <select
              className="select-control"
              value={reviewStatus}
              onChange={(e) => setReviewStatus(e.target.value)}
              disabled={!isReviewer}
            >
              <option value="pending_review">Pending Review (Under Investigation)</option>
              <option value="likely_authentic">Likely Authentic (Human Verified)</option>
              <option value="potentially_manipulated">Potentially Manipulated (Tampering Confirmed)</option>
              <option value="inconclusive">Inconclusive (Insufficient Sensor Quality)</option>
            </select>
            {!isReviewer && (
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                Note: Only certified Reviewers and Administrators can alter the official verdict status.
              </p>
            )}
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Examiner Forensic Notes
            </label>
            <textarea
              className="input-control"
              rows={3}
              placeholder="Record forensic observations, PRNU noise variance, lighting inconsistencies, or audio vocoder phase alignment..."
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              disabled={!isReviewer}
              style={{ resize: 'vertical' }}
            />
          </div>
        </div>

        {isReviewer && (
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              onClick={handleUpdateReviewStatus}
              disabled={updatingReview}
              className="btn btn-primary"
            >
              {updatingReview ? 'Recording Audit Change...' : 'Save Reviewer Determination'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
