import { render, screen } from '@testing-library/react';
import App from './App';

test('renders loading state', () => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: async () => ({ grid: [] }),
    })
  );

  render(<App />);
  const loadingElement = screen.getByText(/chargement de la grille/i);
  expect(loadingElement).toBeInTheDocument();
});
