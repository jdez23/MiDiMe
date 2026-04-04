import { render, screen } from '@testing-library/react';
import App from './App';

jest.mock('./services/api', () => ({
  __esModule: true,
  default: {
    uploadAudioFile: jest.fn(),
    checkHealth: jest.fn(),
  },
}));

test('renders app title', () => {
  render(<App />);
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('MiDiMi');
  expect(screen.getByText(/pattern visualizer/i)).toBeInTheDocument();
});

test('renders visualizer shell before any pattern is loaded', () => {
  render(<App />);
  expect(screen.getByText(/drop audio here/i)).toBeInTheDocument();
  expect(
    screen.getByText(
      /Pick a template to load into the grid. Upload audio to replace/i
    )
  ).toBeInTheDocument();
});
