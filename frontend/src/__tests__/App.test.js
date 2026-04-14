import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';
import { useAuth } from '../context/AuthContext';

jest.mock('../context/AuthContext', () => ({
  AuthProvider: ({ children }) => <div>{children}</div>,
  useAuth: jest.fn(),
}));

jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    Navigate: ({ to }) => <div data-testid="navigate">{to}</div>,
  };
});

const renderApp = () => render(<App />);

describe('App routing', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('redirects unauthenticated user from private route', () => {
    useAuth.mockReturnValue({
      user: null,
      loading: false,
    });
    window.history.pushState({}, 'Test', '/dashboard');
    renderApp();
    expect(screen.getAllByTestId('navigate')[0]).toHaveTextContent('/');
  });

  test('allows authenticated non-admin user to access dashboard', () => {
    useAuth.mockReturnValue({
      user: { is_admin: false },
      loading: false,
    });
    window.history.pushState({}, 'Test', '/dashboard');
    renderApp();
    expect(screen.queryByTestId('navigate')).toBeNull();
  });

  test('redirects admin user to admin dashboard', () => {
    useAuth.mockReturnValue({
      user: { is_admin: true },
      loading: false,
    });
    window.history.pushState({}, 'Test', '/dashboard');
    renderApp();
    expect(screen.getAllByTestId('navigate')[0]).toHaveTextContent(
      '/admin-dashboard'
    );
  });

  test('renders public route when unauthenticated', () => {
    useAuth.mockReturnValue({
      user: null,
      loading: false,
    });
    window.history.pushState({}, 'Test', '/');
    renderApp();
    expect(screen.queryByTestId('navigate')).toBeNull();
  });
});