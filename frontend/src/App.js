import FileUpload from './components/FileUpload';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-gray-900">
            MiDiMe
          </h1>
          <p className="text-gray-600 mt-2">
            Music Pattern Analyzer - Upload your audio files
          </p>
        </div>
      </header>

      <main className="py-12">
        <FileUpload />
      </main>

      <footer className="text-center py-8 text-gray-600">
        <p>Phase 1: Foundation Setup - File Upload Demo</p>
      </footer>
    </div>
  );
}

export default App;
