import React from 'react';
import {render, screen} from '@testing-library/react';
import App from '../App';
import {useAuth} from '../context/AuthContext';

jest.mock('../context/AuthContext', () => ({
  AuthProvider: ({children}) => <div>{children}</div>,
  useAuth: jest.fn(),
}));

jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    Navigate: ({to}) => <div data-testid="navigate">{to}</div>,
  };
});

const renderApp = () => render(<App />);

const baseAuth = (overrides = {}) => ({user: null, loading: false, getValidAccessToken: jest.fn().mockResolvedValue('token'), ...overrides});

describe('App routing', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('redirects unauthenticated user from private route', () => {
    useAuth.mockReturnValue(baseAuth({user: null}));
    window.history.pushState({}, 'Test', '/dashboard');
    renderApp();
    expect(screen.getAllByTestId('navigate')[0]).toHaveTextContent('/');
  });

  test('allows authenticated non-admin user to access dashboard', () => {
    useAuth.mockReturnValue(baseAuth({user: { is_admin: false }}));
    window.history.pushState({}, 'Test', '/dashboard');
    renderApp();
    expect(screen.queryByTestId('navigate')).toBeNull();
  });

  test('redirects admin user to admin dashboard', () => {
    useAuth.mockReturnValue(baseAuth({user: { is_admin: true }}));
    window.history.pushState({}, 'Test', '/dashboard');
    renderApp();
    expect(screen.getAllByTestId('navigate')[0]).toHaveTextContent('/admin-dashboard');
  });

  test('renders public route when unauthenticated', () => {
    useAuth.mockReturnValue(baseAuth({user: null}));
    window.history.pushState({}, 'Test', '/');
    renderApp();
    expect(screen.queryByTestId('navigate')).toBeNull();
  });
});