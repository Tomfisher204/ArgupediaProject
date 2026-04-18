import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {useAuth} from '../../context';

const fetchMock = jest.fn();
global.fetch = fetchMock;
window.fetch = fetchMock;

jest.mock('../../context', () => ({useAuth: jest.fn()}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

jest.mock('../../components', () => ({
  Navbar: () => <nav data-testid="navbar" />,
  TrashIcon: () => <span data-testid="trash-icon" />,
  ThemeRequestForm: ({onClose, onSuccess}) => (
    <div data-testid="theme-request-form">
      <button onClick={onSuccess}>form-success</button>
      <button onClick={onClose}>form-close</button>
    </div>
  ),
  ConfirmDialog: ({message, onConfirm, onCancel}) => (
    <div data-testid="confirm-dialog">
      <p>{message}</p>
      <button onClick={onConfirm}>confirm</button>
      <button onClick={onCancel}>cancel</button>
    </div>
  ),
}));

import ThemesPage from '../../pages/ThemesPage';

const mockThemes = [
  {id: 1, title: 'Climate Policy', description: 'Environmental debates', argument_count: 5},
  {id: 2, title: 'AI Ethics', description: '', argument_count: 1},
];

const mockUser = {username: 'alice', is_admin: false};
const mockAdminUser = {username: 'admin', is_admin: true};

const setupFetch = (themes = mockThemes, count = 2) => {
  fetchMock.mockReset();
  fetchMock.mockImplementation((url, options = {}) => {
    const method = options?.method || 'GET';
    const ok = (data) => ({ok: true, status: 200, json: async () => data});
    if (method === 'DELETE') return ok({});
    return ok({results: themes, count, next: null, previous: null});
  });
};

const renderPage = (user = mockUser) => {
  useAuth.mockReturnValue({user, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
  return render(<ThemesPage />);
};

describe('ThemesPage', () => {
  afterEach(() => jest.clearAllMocks());

  test('shows loading message while fetching themes', () => {
    fetchMock.mockReset();
    fetchMock.mockImplementation(() => new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading themes/i)).toBeInTheDocument();
  });

  test('renders theme cards after fetch', async () => {
    setupFetch();
    renderPage();
    expect(await screen.findByText('Climate Policy')).toBeInTheDocument();
    expect(screen.getByText('AI Ethics')).toBeInTheDocument();
    expect(screen.getByText(/5 arguments/i)).toBeInTheDocument();
    expect(screen.getByText(/1 argument$/i)).toBeInTheDocument();
  });

  test('renders theme description when present', async () => {
    setupFetch();
    renderPage();
    expect(await screen.findByText('Environmental debates')).toBeInTheDocument();
  });

  test('shows empty state when no themes are returned', async () => {
    setupFetch([], 0);
    renderPage();
    await waitFor(() => expect(screen.getByText(/no themes yet/i)).toBeInTheDocument());
  });

  test('shows error message when fetch fails', async () => {
    fetchMock.mockReset();
    fetchMock.mockResolvedValue({ok: false, json: async () => ({})});
    renderPage();
    await waitFor(() => expect(screen.getByText(/failed to load themes/i)).toBeInTheDocument());
  });

  test('navigates to theme arguments page when a card is clicked', async () => {
    const navigate = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(navigate);
    setupFetch();
    renderPage();
    fireEvent.click(await screen.findByText('Climate Policy'));
    expect(navigate).toHaveBeenCalledWith('/themes/1');
  });

  test('opens ThemeRequestForm when Request a Theme is clicked', async () => {
    setupFetch();
    renderPage();
    await screen.findByText('Climate Policy');
    fireEvent.click(screen.getByRole('button', {name: /request a theme/i}));
    expect(screen.getByTestId('theme-request-form')).toBeInTheDocument();
  });

  test('closes form and refetches on form success', async () => {
    setupFetch();
    renderPage();
    await screen.findByText('Climate Policy');
    fireEvent.click(screen.getByRole('button', {name: /request a theme/i}));
    fireEvent.click(screen.getByRole('button', {name: /form-success/i}));
    await waitFor(() => expect(screen.queryByTestId('theme-request-form')).not.toBeInTheDocument());
    expect(fetchMock.mock.calls.length).toBeGreaterThan(1);
  });

  test('closes form without refetching when form-close is clicked', async () => {
    setupFetch();
    renderPage();
    await screen.findByText('Climate Policy');
    fireEvent.click(screen.getByRole('button', {name: /request a theme/i}));
    const callsBefore = fetchMock.mock.calls.length;
    fireEvent.click(screen.getByRole('button', {name: /form-close/i}));
    expect(screen.queryByTestId('theme-request-form')).not.toBeInTheDocument();
    expect(fetchMock.mock.calls.length).toBe(callsBefore);
  });

  test('does not show delete buttons for non-admin users', async () => {
    setupFetch();
    renderPage(mockUser);
    await screen.findByText('Climate Policy');
    expect(screen.queryByTestId('trash-icon')).not.toBeInTheDocument();
  });

  test('shows delete buttons for admin users', async () => {
    setupFetch();
    renderPage(mockAdminUser);
    await screen.findByText('Climate Policy');
    expect(screen.getAllByTestId('trash-icon').length).toBeGreaterThan(0);
  });

  test('shows confirm dialog when delete button is clicked', async () => {
    setupFetch();
    renderPage(mockAdminUser);
    const trashButtons = await screen.findAllByTestId('trash-icon');
    fireEvent.click(trashButtons[0]);
    expect(await screen.findByTestId('confirm-dialog')).toBeInTheDocument();
    expect(screen.getByText(/are you sure you want to delete this theme/i)).toBeInTheDocument();
  });

  test('sends DELETE request and refetches on confirm', async () => {
    setupFetch();
    renderPage(mockAdminUser);
    const trashButtons = await screen.findAllByTestId('trash-icon');
    fireEvent.click(trashButtons[0]);
    fireEvent.click(await screen.findByRole('button', {name: /^confirm$/i}));
    await waitFor(() => {
      const deleteCall = fetchMock.mock.calls.find(([url, opts]) => opts?.method === 'DELETE');
      expect(deleteCall).toBeTruthy();
    });
  });

  test('cancels deletion and dismisses dialog without deleting', async () => {
    setupFetch();
    renderPage(mockAdminUser);
    const trashButtons = await screen.findAllByTestId('trash-icon');
    fireEvent.click(trashButtons[0]);
    fireEvent.click(await screen.findByRole('button', {name: /^cancel$/i}));
    await waitFor(() => expect(screen.queryByTestId('confirm-dialog')).not.toBeInTheDocument());
    expect(fetchMock.mock.calls.every(([, opts]) => opts?.method !== 'DELETE')).toBe(true);
  });

  test('fetches with search query when search input changes', async () => {
    setupFetch();
    renderPage();
    await screen.findByText('Climate Policy');
    fireEvent.change(screen.getByPlaceholderText(/search themes/i), {target: {value: 'climate'}});
    await waitFor(() => {
      const searchCall = fetchMock.mock.calls.find(([url]) => url.includes('q=climate'));
      expect(searchCall).toBeTruthy();
    });
  });

  test('fetches with sort parameter when sort dropdown changes', async () => {
    setupFetch();
    renderPage();
    await screen.findByText('Climate Policy');
    fireEvent.change(screen.getByRole('combobox'), {target: {value: 'date_desc'}});
    await waitFor(() => {
      const sortCall = fetchMock.mock.calls.find(([url]) => url.includes('sort=date_desc'));
      expect(sortCall).toBeTruthy();
    });
  });

  test('hides pagination when all themes fit on one page', async () => {
    setupFetch(mockThemes, 2);
    renderPage();
    await screen.findByText('Climate Policy');
    expect(screen.queryByText(/page 1 of/i)).not.toBeInTheDocument();
  });

  test('shows pagination controls when multiple pages exist', async () => {
    fetchMock.mockReset();
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({results: mockThemes, count: 32, next: 'http://localhost:8000/?page=2', previous: null}),
    });
    renderPage();
    expect(await screen.findByText(/page 1 of 2/i)).toBeInTheDocument();
    expect(screen.getByRole('button', {name: /previous/i})).toBeDisabled();
    expect(screen.getByRole('button', {name: /next/i})).not.toBeDisabled();
  });
});