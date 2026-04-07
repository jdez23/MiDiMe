import DrumDissect from './components/DrumDissect';

function App() {
  return (
    <>
      <div className="grain" aria-hidden="true" />
      <div className="app">
        <header className="app-header">
          <h1 className="app-title app-title--midimi">
            <span className="title-word">
              <span className="glow-letter" data-char="M">
                M
              </span>
              <span className="glow-letter" data-char="i">
                i
              </span>
              <span className="glow-letter" data-char="D">
                D
              </span>
              <span className="glow-letter" data-char="i">
                i
              </span>
              <span className="glow-letter" data-char="M">
                M
              </span>
              <span className="glow-letter" data-char="e">
                e
              </span>
            </span>
          </h1>
          <div className="subtitle">pattern visualizer</div>
        </header>

        <main>
          <DrumDissect />
        </main>

        <footer className="app-footer">MiDiMe by Cycles Studios — Est. 2022</footer>
      </div>
    </>
  );
}

export default App;
