import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

let _backendAvailable = null;
let _healthCheckPromise = null;

const api = {
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

  checkHealth: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`);
      return response.data;
    } catch {
      throw new Error('Backend is not responding');
    }
  },

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
   * Analyse audio via streaming NDJSON.
   *
   * The backend streams progress events as newline-delimited JSON.
   * Each event: { stage, progress (0-1), message, ?pattern }
   *
   * @param {File}          file
   * @param {number}        gridSize
   * @param {number}        barCount
   * @param {number}        [startTime]
   * @param {number}        [endTime]
   * @param {AbortSignal}   [signal]
   * @param {function}      [onProgress]  called with each { stage, progress, message }
   * @returns {Promise<object>} Final pattern object
   */
  analyzeAudio: async (
    file,
    gridSize = 16,
    barCount = 2,
    startTime,
    endTime,
    signal,
    onProgress,
  ) => {
    const formData = new FormData();
    formData.append('audio_file', file);
    formData.append('grid_size', gridSize);
    formData.append('bar_count', barCount);
    if (startTime != null && endTime != null) {
      formData.append('start_time', startTime);
      formData.append('end_time', endTime);
    }

    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
      signal,
      mode: 'cors',
      credentials: 'omit',
    });

    if (!response.ok) {
      let msg = `Server error (${response.status})`;
      try {
        const body = await response.json();
        msg = body.message || msg;
      } catch { /* non-JSON body */ }
      throw new Error(msg);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let pattern = null;

    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.trim()) continue;
        let event;
        try {
          event = JSON.parse(line);
        } catch {
          continue;
        }

        if (event.stage === 'error') {
          throw new Error(event.message || 'Analysis failed');
        }

        if (onProgress) onProgress(event);

        if (event.stage === 'complete' && event.pattern) {
          pattern = event.pattern;
        }
      }
    }

    if (!pattern) {
      throw new Error('No pattern received from server');
    }

    return pattern;
  },
};

export default api;
