import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  UploadCloud, 
  Image as ImageIcon, 
  Video, 
  Mic, 
  FileCheck2, 
  AlertCircle, 
  Clock, 
  ArrowRight,
  ShieldCheck,
  CheckCircle,
  FileQuestion
} from 'lucide-react';
import { analysisAPI } from '../services/api';

export default function MediaAnalysis() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [activeTab, setActiveTab] = useState('image'); // 'image', 'video', 'audio'
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  const [currentStage, setCurrentStage] = useState('');
  const [error, setError] = useState('');
  const [completedJobId, setCompletedJobId] = useState(null);

  const mediaConfig = {
    image: {
      title: 'Image Authenticity & Splicing Analysis',
      acceptedExts: '.jpg, .jpeg, .png, .webp',
      acceptedMime: ['image/jpeg', 'image/png', 'image/webp'],
      maxSizeMb: 50,
      icon: ImageIcon,
      description: 'Upload suspicious face photos, avatars, or identity documents for Error Level Analysis (ELA) and 2D-FFT frequency spectrum inspection.'
    },
    video: {
      title: 'Video Deepfake & Face-Swap Analysis',
      acceptedExts: '.mp4, .avi, .mov, .mkv',
      acceptedMime: ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska'],
      maxSizeMb: 100,
      icon: Video,
      description: 'Upload video clips for frame sampling, face tracking, temporal flicker evaluation, and suspicious thumbnail extraction.'
    },
    audio: {
      title: 'Synthetic Speech & Voice Clone Detection',
      acceptedExts: '.wav, .mp3, .flac',
      acceptedMime: ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/x-wav', 'audio/flac'],
      maxSizeMb: 50,
      icon: Mic,
      description: 'Upload speech recordings for STFT Wiener entropy, harmonic continuity checks, and neural vocoder (HiFi-GAN, WaveNet) detection.'
    }
  };

  const currentConfig = mediaConfig[activeTab];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (file) => {
    setError('');
    setCompletedJobId(null);
    if (!file) return;

    // Validate size
    const maxBytes = currentConfig.maxSizeMb * 1024 * 1024;
    if (file.size > maxBytes) {
      setError(`File size (${(file.size / (1024*1024)).toFixed(1)} MB) exceeds maximum limit of ${currentConfig.maxSizeMb} MB.`);
      return;
    }

    setSelectedFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const pollJobStatus = async (jobId) => {
    const maxAttempts = 40;
    let attempts = 0;

    const interval = setInterval(async () => {
      attempts++;
      try {
        const res = await analysisAPI.getStatus(jobId);
        const data = res.data;

        if (data.status === 'completed') {
          clearInterval(interval);
          setAnalyzing(false);
          setCompletedJobId(jobId);
          setCurrentStage('Analysis complete. Redirecting to forensic viewer...');
          setTimeout(() => {
            navigate(`/analysis/${jobId}`);
          }, 1000);
        } else if (data.status === 'failed') {
          clearInterval(interval);
          setAnalyzing(false);
          setError(`Inference failed: ${data.error_message || 'Model encountered an error processing the media file.'}`);
        } else {
          // Dynamic stage progression text
          if (activeTab === 'image') {
            if (attempts < 3) setCurrentStage('Safely decoding image and extracting EXIF headers...');
            else if (attempts < 6) setCurrentStage('Computing Error Level Analysis (ELA) compression residual map...');
            else if (attempts < 9) setCurrentStage('Generating 2D-FFT high-frequency power spectrum...');
            else setCurrentStage('Running MesoInception-4 neural inference and uncertainty calibration...');
          } else if (activeTab === 'video') {
            if (attempts < 4) setCurrentStage('Extracting video frames and tracking face bounding boxes...');
            else if (attempts < 8) setCurrentStage('Analyzing inter-frame temporal flicker and facial jitter...');
            else setCurrentStage('Pooling frame scores and generating forensic thumbnails...');
          } else {
            if (attempts < 4) setCurrentStage('Decoding PCM audio and computing Short-Time Fourier Transform...');
            else setCurrentStage('Calculating STFT Wiener entropy and vocoder anomaly indices...');
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }

      if (attempts >= maxAttempts) {
        clearInterval(interval);
        setAnalyzing(false);
        setError('Analysis timed out. You can review job progress in your History dashboard.');
      }
    }, 1500);
  };

  const handleStartAnalysis = async () => {
    if (!selectedFile) return;

    setError('');
    setAnalyzing(true);
    setUploadProgress(0);
    setCurrentStage('Uploading media securely to forensic storage...');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      let res;
      if (activeTab === 'image') {
        res = await analysisAPI.analyzeImageDirect(formData, (p) => setUploadProgress(p));
      } else if (activeTab === 'video') {
        res = await analysisAPI.analyzeVideoDirect(formData, (p) => setUploadProgress(p));
      } else {
        res = await analysisAPI.analyzeAudioDirect(formData, (p) => setUploadProgress(p));
      }

      const jobId = res.data.id;
      setCurrentStage('Media uploaded. Initializing AI inference workers...');
      pollJobStatus(jobId);
    } catch (err) {
      setAnalyzing(false);
      setError(err.response?.data?.detail || 'Upload failed. Please ensure file format is valid.');
    }
  };

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', padding: '2.5rem 1.5rem' }}>
      {/* Title Header */}
      <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
        <span className="badge badge-cyan" style={{ marginBottom: '0.5rem' }}>EVIDENCE INGESTION</span>
        <h1 style={{ fontSize: '2.2rem', marginBottom: '0.5rem' }}>Media Authenticity Analysis</h1>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '640px', margin: '0 auto' }}>
          Select media modality, upload untrusted files for isolated decoding, and compute verifiable forensic artifact indices.
        </p>
      </div>

      {/* Modality Selector Tabs */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '0.75rem',
        marginBottom: '2rem',
        flexWrap: 'wrap'
      }}>
        {['image', 'video', 'audio'].map((tab) => {
          const cfg = mediaConfig[tab];
          const active = activeTab === tab;
          const Icon = cfg.icon;
          return (
            <button
              key={tab}
              onClick={() => {
                setActiveTab(tab);
                setSelectedFile(null);
                setError('');
                setCompletedJobId(null);
              }}
              disabled={analyzing}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.5rem',
                borderRadius: 'var(--radius-sm)',
                background: active ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%)' : 'rgba(255, 255, 255, 0.03)',
                border: active ? '1px solid var(--cyan-primary)' : '1px solid var(--border-color)',
                color: active ? '#ffffff' : 'var(--text-secondary)',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: analyzing ? 'not-allowed' : 'pointer',
                transition: 'var(--transition-fast)'
              }}
            >
              <Icon size={18} color={active ? 'var(--cyan-primary)' : 'currentColor'} />
              <span>{tab.charAt(0).toUpperCase() + tab.slice(1)} Analysis</span>
            </button>
          );
        })}
      </div>

      {/* Main Upload Box */}
      <div className="glass-panel" style={{ padding: '2.5rem' }}>
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>{currentConfig.title}</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{currentConfig.description}</p>
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

        {/* Drag and Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => !analyzing && fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${dragActive ? 'var(--cyan-primary)' : 'rgba(255, 255, 255, 0.15)'}`,
            borderRadius: 'var(--radius-md)',
            padding: '3.5rem 2rem',
            textAlign: 'center',
            background: dragActive ? 'rgba(6, 182, 212, 0.05)' : 'rgba(0, 0, 0, 0.2)',
            cursor: analyzing ? 'not-allowed' : 'pointer',
            transition: 'var(--transition-fast)',
            position: 'relative'
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={currentConfig.acceptedExts}
            onChange={handleFileInput}
            style={{ display: 'none' }}
            disabled={analyzing}
          />

          <div style={{
            width: '4rem',
            height: '4rem',
            borderRadius: '50%',
            background: 'rgba(6, 182, 212, 0.1)',
            border: '1px solid rgba(6, 182, 212, 0.25)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem',
            boxShadow: 'var(--border-glow)'
          }}>
            <UploadCloud size={32} color="var(--cyan-primary)" />
          </div>

          <h4 style={{ fontSize: '1.1rem', marginBottom: '0.35rem' }}>
            {selectedFile ? selectedFile.name : `Click to browse or drag & drop ${activeTab} file`}
          </h4>

          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Supported formats: {currentConfig.acceptedExts} (Max {currentConfig.maxSizeMb} MB)
          </p>

          {selectedFile && (
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              marginTop: '1rem',
              padding: '0.35rem 0.85rem',
              background: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: 'var(--radius-full)',
              color: 'var(--emerald-safe)',
              fontSize: '0.8rem',
              fontWeight: 600
            }}>
              <CheckCircle size={14} />
              <span>Selected: {(selectedFile.size / (1024*1024)).toFixed(2)} MB</span>
            </div>
          )}
        </div>

        {/* Live Analysis Progress Container */}
        {analyzing && (
          <div style={{ marginTop: '2rem', padding: '1.25rem', background: 'rgba(0, 0, 0, 0.3)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
              <span style={{ color: 'var(--cyan-primary)', fontWeight: 600 }}>{currentStage}</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>{uploadProgress}%</span>
            </div>

            {/* Progress bar */}
            <div style={{ width: '100%', height: '8px', background: '#1e293b', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{
                width: `${uploadProgress}%`,
                height: '100%',
                background: 'linear-gradient(90deg, #06b6d4, #3b82f6)',
                transition: 'width 0.3s ease'
              }} />
            </div>

            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
              Background AI workers are computing feature maps. This usually takes 3 to 10 seconds.
            </p>
          </div>
        )}

        {/* Action Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2rem' }}>
          <button
            onClick={handleStartAnalysis}
            disabled={!selectedFile || analyzing}
            className="btn btn-primary"
            style={{
              padding: '0.875rem 2.25rem',
              fontSize: '0.95rem',
              opacity: (!selectedFile || analyzing) ? 0.5 : 1,
              cursor: (!selectedFile || analyzing) ? 'not-allowed' : 'pointer'
            }}
          >
            {analyzing ? 'Running Forensic Pipeline...' : 'Execute AI Detection Pipeline'}
            <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
