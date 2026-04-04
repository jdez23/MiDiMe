import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

let _backendAvailable = null;
let _healthCheckPromise = null;

const api = {
  /**
   * Upload an audio file to the backend.
   */
  uploadAudioFile: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('audio_file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: onUploadProgress
          ? (progressEvent) => {
              const pct = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              onUploadProgress(pct);
            }
          : undefined,
      });
      return response.data;
    } catch (error) {
      if (error.response?.data) {
        throw new Error(
          error.response.data.message ||
            JSON.stringify(error.response.data.errors) ||
            'Upload failed'
        );
      }
      throw new Error(error.message || 'Network error');
    }
  },

  /**
   * Check backend health. Result is cached for the session.
   */
  checkHealth: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`);
      return response.data;
    } catch {
      throw new Error('Backend is not responding');
    }
  },

  /**
   * Returns true if the backend /api/health endpoint responds.
   * Caches the result so subsequent calls are instant.
   */
  isBackendAvailable: async () => {
    if (_backendAvailable !== null) return _backendAvailable;
    if (!_healthCheckPromise) {
      _healthCheckPromise = axios
        .get(`${API_BASE_URL}/api/health`, { timeout: 3000 })
        .then(() => {
          _backendAvailable = true;
          return true;
        })
        .catch(() => {
          _backendAvailable = false;
          return false;
        });
    }
    return _healthCheckPromise;
  },

  /**
   * Send an audio file to the backend for drum analysis.
   *
   * @param {File} file            Audio file
   * @param {number} gridSize      Steps per bar (8 | 16 | 32)
   * @param {number} barCount      Number of bars (1 | 2 | 4)
   * @param {number} [startTime]   Region start in seconds (optional)
   * @param {number} [endTime]     Region end in seconds (optional)
   * @returns {Promise<object>}    Pattern object ready for DrumDissect
   */
  analyzeAudio: async (file, gridSize = 16, barCount = 2, startTime, endTime) => {
    const formData = new FormData();
    formData.append('audio_file', file);
    formData.append('grid_size', gridSize);
    formData.append('bar_count', barCount);
    if (startTime != null && endTime != null) {
      formData.append('start_time', startTime);
      formData.append('end_time', endTime);
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/api/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120_000,
      });

      const data = response.data;
      if (data.status !== 'success') {
        throw new Error(data.message || 'Analysis failed');
      }
      return data.pattern;
    } catch (error) {
      if (error.response?.data) {
        throw new Error(
          error.response.data.message ||
            JSON.stringify(error.response.data.errors) ||
            'Analysis failed'
        );
      }
      throw new Error(error.message || 'Network error');
    }
  },
};

export default api;
