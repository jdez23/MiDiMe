const LoadingSpinner = ({ message = 'Loading…', overlay = false }) => {
  if (overlay) {
    return (
      <div className="loading-overlay active" role="status" aria-live="polite">
        <div className="loading-orb" />
        <div className="loading-text">{message}</div>
      </div>
    );
  }

  return (
    <div className="loading-stack" role="status" aria-live="polite">
      <div className="loading-orb" />
      <div className="loading-text">{message}</div>
    </div>
  );
};

export default LoadingSpinner;
