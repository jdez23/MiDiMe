import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * API service for communicating with the Django backend
 */
const api = {
  /**
   * Upload an audio file to the backend
   * @param {File} file - The audio file to upload
   * @param {Function} onUploadProgress - Optional callback for upload progress
   * @returns {Promise} Response data from the server
   */
  uploadAudioFile: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('audio_file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: onUploadProgress ? (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onUploadProgress(percentCompleted);
        } : undefined,
      });

      return response.data;
    } catch (error) {
      // Extract error message from response
      if (error.response && error.response.data) {
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
   * Check the health of the backend API
   * @returns {Promise} Health status
   */
  checkHealth: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`);
      return response.data;
    } catch (error) {
      throw new Error('Backend is not responding');
    }
  },
};

export default api;
