import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {useAuth} from '../../context/AuthContext';
import Dashboard from '../../pages/Dashboard';

jest.mock('../../context/AuthContext', () => ({useAuth: jest.fn()}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Navigate: ({to}) => <div data-testid="navigate">{to}</div>,
  useNavigate: () => jest.fn(),
}));

jest.mock('../../components', () => ({Navbar: () => <nav data-testid="navbar" />}));

const mockArguments = (count = 2) =>
  Array.from({length: count}, (_, i) => ({
    id: i + 1,
    theme: `Theme ${i + 1}`,
    scheme_name: `Scheme ${i + 1}`,
    scheme_template: '**Premise**: **P1**',
    field_values: [{field_name: 'P1', value: `Value ${i + 1}`}],
    date_created: '2024-01-01T00:00:00Z',
    child_count: i,
  }));

const mockUser = {username: 'alice', email: 'alice@example.com', date_joined: '2023-06-15T00:00:00Z', argument_count: 5, reputation: 8, win_rate: 60};

const setupFetch = (args = mockArguments(), totalCount = 2) => {
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => ({results: args, count: totalCount, next: null, previous: null}),
  });
};

const renderPage = () => render(<Dashboard />);

describe('Dashboard', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  test('shows loading state while auth resolves', () => {
    useAuth.mockReturnValue({user: mockUser, loading: true, getValidAccessToken: jest.fn()});
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('redirects unauthenticated user to root', () => {
    useAuth.mockReturnValue({user: null, loading: false, getValidAccessToken: jest.fn()});
    renderPage();
    expect(screen.getByTestId('navigate')).toHaveTextContent('/');
  });

  test('renders user profile section', async () => {
    setupFetch();
    useAuth.mockReturnValue({user: mockUser, loading: false, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    renderPage();
    expect(await screen.findByText('alice')).toBeInTheDocument();
    expect(screen.getByText('alice@example.com')).toBeInTheDocument();
    expect(screen.getByText(/June 2023/i)).toBeInTheDocument();
  });

  test('renders argument cards', async () => {
    setupFetch();
    useAuth.mockReturnValue({user: mockUser, loading: false, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    renderPage();
    await expect(screen.findByText('Theme 1')).resolves.toBeInTheDocument();
  });

  test('shows empty state when no arguments', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: true, json: async () => ({results: [], count: 0})});
    useAuth.mockReturnValue({user: mockUser, loading: false, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    renderPage();
    await waitFor(() => {expect(screen.getByText(/haven't created any arguments/i)).toBeInTheDocument()});
  });
});