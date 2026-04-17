import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {useAuth} from '../../context/AuthContext';
import LandingPage from '../../pages/LandingPage';

jest.mock('../../context/AuthContext', () => ({useAuth: jest.fn()}));

jest.mock('react-router-dom', () => ({...jest.requireActual('react-router-dom'), Navigate: ({to}) => <div data-testid="navigate">{to}</div>}));

const renderPage = () => render(<LandingPage />);

describe('LandingPage', () => {
  afterEach(() => jest.clearAllMocks());

  test('shows loading state while auth is resolving', () => {
    useAuth.mockReturnValue({user: null, loading: true, error: null, login: jest.fn(), signup: jest.fn()});
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('redirects authenticated user to dashboard', () => {
    useAuth.mockReturnValue({user: {username: 'alice'}, loading: false, error: null, login: jest.fn(), signup: jest.fn()});
    renderPage();
    expect(screen.getByTestId('navigate')).toHaveTextContent('/dashboard');
  });

  test('renders marketing content and auth form for unauthenticated user', () => {
    useAuth.mockReturnValue({user: null, loading: false, error: null, login: jest.fn(), signup: jest.fn()});
    renderPage();
    expect(screen.getByText(/argumentation done right/i)).toBeInTheDocument();
    expect(screen.getByText(/A structured debate platform/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  test('switches to signup mode and shows extra fields', () => {
    useAuth.mockReturnValue({user: null, loading: false, error: null, login: jest.fn(), signup: jest.fn()});
    renderPage();
    fireEvent.click(screen.getAllByRole('button', {name: /sign up/i})[0]);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
  });

  test('calls login with form values on submit', async () => {
    const login = jest.fn().mockResolvedValue();
    useAuth.mockReturnValue({user: null, loading: false, error: null, login, signup: jest.fn()});
    renderPage();
    fireEvent.change(screen.getByLabelText(/username/i), {target: {name: 'username', value: 'bob'}});
    fireEvent.change(screen.getByLabelText(/password/i), {target: {name: 'password', value: 'secret'}});
    fireEvent.click(screen.getAllByRole('button', {name: /log in/i})[1]);
    await waitFor(() => expect(login).toHaveBeenCalledWith('bob', 'secret'));
  });

  test('calls signup with all fields when in signup mode', async () => {
    const signup = jest.fn().mockResolvedValue();
    useAuth.mockReturnValue({user: null, loading: false, error: null, login: jest.fn(), signup});
    renderPage();
    fireEvent.click(screen.getAllByRole('button', {name: /sign up/i})[0]);
    fireEvent.change(screen.getByLabelText(/username/i), {target: {name: 'username', value: 'carol'}});
    fireEvent.change(screen.getByLabelText(/email/i), {target: {name: 'email', value: 'c@e.com'}});
    fireEvent.change(screen.getByLabelText(/first name/i), {target: {name: 'first_name', value: 'Carol'}});
    fireEvent.change(screen.getByLabelText(/last name/i), {target: {name: 'last_name', value: 'Smith'}});
    fireEvent.change(screen.getByLabelText(/password/i), {target: {name: 'password', value: 'pw'}});
    fireEvent.click(screen.getAllByRole('button', {name: /create account/i})[0]);
    await waitFor(() => expect(signup).toHaveBeenCalledWith('carol', 'c@e.com', 'pw', 'Carol', 'Smith'));
  });

  test('displays error message when login throws', async () => {
    const login = jest.fn().mockRejectedValue(new Error('Invalid credentials'));
    useAuth.mockReturnValue({user: null, loading: false, error: null, login, signup: jest.fn()});
    renderPage();
    fireEvent.change(screen.getByLabelText(/username/i), {target: {name: 'username', value: 'x'}});
    fireEvent.change(screen.getByLabelText(/password/i), {target: {name: 'password', value: 'y'}});
    fireEvent.click(screen.getAllByRole('button', {name: /log in/i})[1]);
    await waitFor(() => expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument());
  });

  test('displays context-level error from useAuth', () => {
    useAuth.mockReturnValue({user: null, loading: false, error: 'Server error', login: jest.fn(), signup: jest.fn()});
    renderPage();
    expect(screen.getByText(/server error/i)).toBeInTheDocument();
  });

  test('clears form values when switching between login and signup tabs', () => {
    useAuth.mockReturnValue({user: null, loading: false, error: null, login: jest.fn(), signup: jest.fn()});
    renderPage();
    fireEvent.change(screen.getByLabelText(/username/i), {target: {name: 'username', value: 'dave'}});
    fireEvent.click(screen.getAllByRole('button', {name: /sign up/i})[0]);
    expect(screen.getByLabelText(/username/i).value).toBe('');
  });
});