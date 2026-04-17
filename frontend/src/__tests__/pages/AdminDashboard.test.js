import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {useAuth} from '../../context';

const fetchMock = jest.fn();
global.fetch = fetchMock;
window.fetch = fetchMock;

import AdminDashboard from '../../pages/AdminDashboard';

jest.mock('../../context', () => ({useAuth: jest.fn()}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Navigate: ({to}) => <div data-testid="navigate">{to}</div>,
  useNavigate: () => jest.fn(),
}));

jest.mock('../../components', () => ({Navbar: () => <nav data-testid="navbar" />}));

const mockStats = {total_users: 42, total_arguments: 100, total_themes: 10, pending_theme_requests: 3};

const mockThemeRequests = [
  {id: 1, title: 'Climate Change', status: 'pending', description: 'A debate theme', reason: 'Popular topic', requested_by: {username: 'bob'}, date_created: '2024-03-01T00:00:00Z'},
  {id: 2, title: 'AI Ethics', status: 'pending', description: 'Tech ethics', reason: 'Timely', requested_by: {username: 'carol'}, date_created: '2024-03-02T00:00:00Z'}
];

const mockReportedArgs = [
  {id: 10, scheme_name: 'Expert Opinion', scheme_template: '**Expert** says **Claim**', field_values: [{field_name: 'Expert', value: 'Dr. Smith'}, {field_name: 'Claim', value: 'Vaccines work'}], report_count: 5, author: 'dave', theme: 'Health'}
];

const mockUser = {username: 'admin', is_admin: true};

const setupFetch = () => {
  fetchMock.mockReset();
  fetchMock.mockImplementation((url, options = {}) => {
    const method = options?.method || 'GET';
    const okResponse = (data) => ({ok: true, status: 200, json: async () => data});
    if (!url) return okResponse({});
    if (method === 'POST') return okResponse({});
    if (url.includes('/stats')) return okResponse(mockStats);
    if (url.includes('/theme-requests') && !url.match(/theme-requests\/\d+/)) return okResponse({results: mockThemeRequests, count: 2, next: null, previous: null});
    if (url.match(/theme-requests\/\d+/)) return okResponse(mockThemeRequests[0]);
    if (url.includes('/reported-arguments')) return okResponse({results: mockReportedArgs, count: 1, next: null, previous: null});
    return okResponse({});
  });
};

const renderPage = () => render(<AdminDashboard />);

describe('AdminDashboard', () => {
  afterEach(() => jest.clearAllMocks());

  test('redirects unauthenticated user to root', () => {
    useAuth.mockReturnValue({user: null, loading: false, getValidAccessToken: jest.fn()});
    renderPage();
    expect(screen.getByTestId('navigate')).toHaveTextContent('/');
  });

  test('renders stat cards with values from the stats endpoint', async () => {
    setupFetch();
    useAuth.mockReturnValue({user: mockUser, loading: false, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    renderPage();
    await waitFor(() => {expect(screen.getByText('42')).toBeInTheDocument();});
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  test('renders pending theme request cards', async () => {
    setupFetch();
    useAuth.mockReturnValue({user: mockUser, loading: false, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    renderPage();
    expect(await screen.findByText('Climate Change')).toBeInTheDocument();
    expect(screen.getByText('AI Ethics')).toBeInTheDocument();
  });

  test('opens modal with full request details on card click', async () => {
    setupFetch();
    useAuth.mockReturnValue({user: mockUser, loading: false, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    renderPage();
    const card = await screen.findByText('Climate Change');
    fireEvent.click(card);
    expect(await screen.findByText(/a debate theme/i)).toBeInTheDocument();
    expect(await screen.findByText(/popular topic/i)).toBeInTheDocument();
    expect(await screen.findByText(/bob/i)).toBeInTheDocument();
  });
});