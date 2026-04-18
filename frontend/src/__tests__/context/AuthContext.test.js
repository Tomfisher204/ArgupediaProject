import React from 'react';
import {render, screen, fireEvent, waitFor, act} from '@testing-library/react';

jest.unmock('../../context');
jest.unmock('../../context/AuthContext');

import {AuthProvider, useAuth} from '../../context/AuthContext';

const fetchMock = jest.fn();
global.fetch = fetchMock;
window.fetch = fetchMock;

const makeJwt = (expOffsetSeconds = 3600) => {
  const payload = {exp: Math.floor(Date.now() / 1000) + expOffsetSeconds};
  const encoded = btoa(JSON.stringify(payload));
  return `header.${encoded}.signature`;
};

const expiredJwt = makeJwt(-100);
const validJwt = makeJwt(3600);
const freshJwt = makeJwt(7200);

const setStoredTokens = (access = validJwt, refresh = 'refresh-token') => {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
};

const clearStoredTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

const TestConsumer = () => {
  const {user, loading, error, login, signup, logout} = useAuth();
  return (
    <div>
      {loading && <p data-testid="loading">loading</p>}
      {user && <p data-testid="user">{user.username}</p>}
      {error && <p data-testid="error">{error}</p>}
      <button onClick={() => login('alice', 'pass')}>login</button>
      <button onClick={() => signup('alice', 'a@b.com', 'pass', 'Alice', 'Smith')}>signup</button>
      <button onClick={logout}>logout</button>
    </div>
  );
};

const renderProvider = () => render(<AuthProvider><TestConsumer /></AuthProvider>);

describe('AuthContext', () => {
  beforeEach(() => {
    clearStoredTokens();
    fetchMock.mockReset();
  });

  afterEach(() => jest.clearAllMocks());

  // When there are no tokens in localStorage the provider should finish
  // loading immediately with user set to null.
  test('sets loading to false and user to null when no tokens stored', async () => {
    renderProvider();
    await waitFor(() => expect(screen.queryByTestId('loading')).not.toBeInTheDocument());
    expect(screen.queryByTestId('user')).not.toBeInTheDocument();
  });

  // When a valid (non-expired) access token is stored along with a refresh
  // token, the provider should fetch the user profile on mount and populate
  // the user state.
  test('restores session from stored valid token on mount', async () => {
    setStoredTokens(validJwt);
    fetchMock.mockResolvedValue({ok: true, json: async () => ({username: 'alice'})});
    renderProvider();
    expect(await screen.findByTestId('user')).toHaveTextContent('alice');
  });

  // When the stored access token is expired the provider should use the
  // refresh token to get a new access token before fetching the user profile.
  test('refreshes expired access token on mount then fetches user', async () => {
    setStoredTokens(expiredJwt);
    fetchMock
      .mockResolvedValueOnce({ok: true, json: async () => ({access: freshJwt, refresh: null})})
      .mockResolvedValueOnce({ok: true, json: async () => ({username: 'alice'})});
    renderProvider();
    expect(await screen.findByTestId('user')).toHaveTextContent('alice');
    const refreshCall = fetchMock.mock.calls.find(([url]) => url.includes('/api/token/refresh/'));
    expect(refreshCall).toBeTruthy();
  });

  // If restoring the session fails (e.g. refresh token is invalid), tokens
  // should be cleared from localStorage and user should remain null.
  test('clears tokens and leaves user null when session restore fails', async () => {
    setStoredTokens(expiredJwt);
    fetchMock.mockResolvedValue({ok: false, json: async () => ({})});
    renderProvider();
    await waitFor(() => expect(screen.queryByTestId('loading')).not.toBeInTheDocument());
    expect(screen.queryByTestId('user')).not.toBeInTheDocument();
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
  });

  // A successful login should store the returned tokens, fetch the user
  // profile, and populate user state.
  test('login stores tokens and sets user on success', async () => {
    fetchMock
      .mockResolvedValueOnce({ok: true, json: async () => ({access: validJwt, refresh: 'r'})})
      .mockResolvedValueOnce({ok: true, json: async () => ({username: 'alice'})});
    renderProvider();
    await waitFor(() => expect(screen.queryByTestId('loading')).not.toBeInTheDocument());
    await act(async () => {fireEvent.click(screen.getByRole('button', {name: /^login$/i}));});
    expect(await screen.findByTestId('user')).toHaveTextContent('alice');
    expect(localStorage.getItem('access_token')).toBe(validJwt);
  });

  // When login credentials are wrong the API returns a non-ok response,
  // the error state should be set and user should remain null.
  test('login sets error state on failed credentials', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    fetchMock.mockResolvedValue({ok: false, json: async () => ({detail: 'No active account found.'})});
    renderProvider();
    await waitFor(() => expect(screen.queryByTestId('loading')).not.toBeInTheDocument());
    await act(async () => {
      fireEvent.click(screen.getByRole('button', {name: /^login$/i}));
      await Promise.resolve();
    }).catch(() => {});
    expect(await screen.findByTestId('error')).toHaveTextContent('No active account found.');
    expect(screen.queryByTestId('user')).not.toBeInTheDocument();
    consoleError.mockRestore();
  });

  // A successful signup should call the register endpoint and then
  // automatically call login so the user ends up authenticated.
  test('signup calls register then logs in automatically', async () => {
    fetchMock
      .mockResolvedValueOnce({ok: true, json: async () => ({})})
      .mockResolvedValueOnce({ok: true, json: async () => ({access: validJwt, refresh: 'r'})})
      .mockResolvedValueOnce({ok: true, json: async () => ({username: 'alice'})});
    renderProvider();
    await waitFor(() => expect(screen.queryByTestId('loading')).not.toBeInTheDocument());
    await act(async () => {fireEvent.click(screen.getByRole('button', {name: /^signup$/i}));});
    expect(await screen.findByTestId('user')).toHaveTextContent('alice');
    const registerCall = fetchMock.mock.calls.find(([url]) => url.includes('/api/auth/register/'));
    expect(registerCall).toBeTruthy();
  });

  // When signup fails the API error message should be extracted from the
  // response and set as the error state.
  test('signup sets error state on failed registration', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    fetchMock.mockResolvedValue({ok: false, json: async () => ({username: ['A user with that username already exists.']})});
    renderProvider();
    await waitFor(() => expect(screen.queryByTestId('loading')).not.toBeInTheDocument());
    await act(async () => {
      fireEvent.click(screen.getByRole('button', {name: /^signup$/i}));
      await Promise.resolve();
    }).catch(() => {});
    expect(await screen.findByTestId('error')).toHaveTextContent('A user with that username already exists.');
    consoleError.mockRestore();
  });
});