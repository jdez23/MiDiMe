import { useCallback, useRef, useState } from 'react';
import api from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const FileUpload = ({ embedded = false }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setError(null);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    const file = event.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setError(null);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);
    setUploadProgress(0);

    try {
      const response = await api.uploadAudioFile(selectedFile, (progress) =>
        setUploadProgress(progress)
      );

      setResult(response);
      setUploading(false);
    } catch (err) {
      setError(err.message);
      setUploading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setResult(null);
    setError(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${Math.round((bytes / k ** i) * 100) / 100} ${sizes[i]}`;
  };

  const openFilePicker = () => fileInputRef.current?.click();

  const shellClass = `drop-zone-shell${dragOver ? ' drop-zone-shell--dragover' : ''}`;

  return (
    <div>
      {!embedded ? (
        <div className="section-header">
          <span className="section-title">Upload Audio</span>
          <div className="section-line" />
        </div>
      ) : null}

      <div
        className={shellClass}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <div className="drop-zone-blob" aria-hidden="true" />
        <div
          role="button"
          tabIndex={0}
          className="drop-zone-content"
          onClick={openFilePicker}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              openFilePicker();
            }
          }}
        >
          <span className="drop-icon">~</span>
          <div className="drop-text">
            <strong>drop audio here</strong>
            <br />
            or tap to browse
          </div>
          <div className="drop-hint">mp3 · wav · flac · m4a · ogg</div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".mp3,.wav,.flac,.m4a,.ogg,audio/*"
            onChange={handleFileSelect}
            className="visually-hidden-input"
            aria-label="Choose audio file"
          />
        </div>
      </div>

      {selectedFile && (
        <div className="file-meta-grid">
          <div className="info-card">
            <div className="info-card-label">Selected file</div>
            <div className="info-card-value">{selectedFile.name}</div>
            <div className="info-card-detail">{formatFileSize(selectedFile.size)}</div>
            <button type="button" className="text-link" onClick={handleReset}>
              Remove
            </button>
          </div>
        </div>
      )}

      {selectedFile && !uploading && !result && (
        <button type="button" className="export-btn export-btn--block" onClick={handleUpload}>
          Send to server
        </button>
      )}

      {uploading && (
        <LoadingSpinner overlay message={`Uploading… ${uploadProgress}%`} />
      )}

      {result && result.status === 'success' && (
        <>
          <div className="section-header section-spaced">
            <span className="section-title">Response</span>
            <div className="section-line" />
          </div>
          <div className="pattern-desc pattern-desc--success">
            <div className="panel-heading">Upload successful</div>
            <div className="panel-body">{result.message}</div>
            {result.data && (
              <div className="file-meta-grid meta-nested">
                <div className="info-card">
                  <div className="info-card-label">Filename</div>
                  <div className="info-card-value">{result.data.filename}</div>
                </div>
                <div className="info-card">
                  <div className="info-card-label">Size</div>
                  <div className="info-card-value">{result.data.file_size}</div>
                </div>
              </div>
            )}
            <button type="button" className="text-link" onClick={handleReset}>
              Upload another file
            </button>
          </div>
        </>
      )}

      {error && (
        <div className="pattern-desc pattern-desc--error alert-block">
          <div className="panel-heading">Upload failed</div>
          <div className="panel-body">{error}</div>
          <button type="button" className="text-link" onClick={handleReset}>
            Try again
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
