import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {useAuth} from '../../context';
import ThemeRequestForm from '../../components/ThemeRequestForm';

jest.mock('../../context', () => ({useAuth: jest.fn()}));

const mockGetToken = jest.fn().mockResolvedValue('test-token');

const renderForm = (overrides = {}) => {
  useAuth.mockReturnValue({getValidAccessToken: mockGetToken});
  const props = {onClose: jest.fn(), onSuccess: jest.fn(), ...overrides};
  render(<ThemeRequestForm {...props} />);
  return props;
};

describe('ThemeRequestForm', () => {
  afterEach(() => jest.clearAllMocks());

  test('renders the form title and all input fields', () => {
    renderForm();
    expect(screen.getByText(/request a theme/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/theme title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/why should this be added/i)).toBeInTheDocument();
  });

  test('shows validation error when title is empty', async () => {
    renderForm();
    fireEvent.click(screen.getByRole('button', {name: /submit request/i}));
    expect(await screen.findByText(/title is required/i)).toBeInTheDocument();
    expect(mockGetToken).not.toHaveBeenCalled();
  });

  test('shows validation error when reason is empty', async () => {
    renderForm();
    fireEvent.change(screen.getByLabelText(/theme title/i), {target: {name: 'title', value: 'My Theme'}});
    fireEvent.click(screen.getByRole('button', {name: /submit request/i}));
    expect(await screen.findByText(/please explain why/i)).toBeInTheDocument();
    expect(mockGetToken).not.toHaveBeenCalled();
  });

  test('calls onSuccess after a successful submission', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: true});
    const {onSuccess} = renderForm();
    fireEvent.change(screen.getByLabelText(/theme title/i), {target: {name: 'title', value: 'Climate Policy'}});
    fireEvent.change(screen.getByLabelText(/why should this be added/i), {target: {name: 'reason', value: 'Very relevant topic'}});
    fireEvent.click(screen.getByRole('button', {name: /submit request/i}));
    await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1));
  });

  test('POSTs the correct form data to the API', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: true});
    renderForm();
    fireEvent.change(screen.getByLabelText(/theme title/i), {target: {name: 'title', value: 'AI Ethics'}});
    fireEvent.change(screen.getByLabelText(/description/i), {target: {name: 'description', value: 'Tech debates'}});
    fireEvent.change(screen.getByLabelText(/why should this be added/i), {target: {name: 'reason', value: 'Timely topic'}});
    fireEvent.click(screen.getByRole('button', {name: /submit request/i}));
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    const body = JSON.parse(global.fetch.mock.calls[0][1].body);
    expect(body).toEqual({title: 'AI Ethics', description: 'Tech debates', reason: 'Timely topic'});
  });

  test('shows API error message on failed submission', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: false, json: async () => ({title: ['This title already exists.']})});
    renderForm();
    fireEvent.change(screen.getByLabelText(/theme title/i), {target: {name: 'title', value: 'Duplicate'}});
    fireEvent.change(screen.getByLabelText(/why should this be added/i), {target: {name: 'reason', value: 'reason here'}});
    fireEvent.click(screen.getByRole('button', {name: /submit request/i}));
    expect(await screen.findByText(/this title already exists/i)).toBeInTheDocument();
  });

  test('calls onClose when Cancel is clicked', () => {
    const {onClose} = renderForm();
    fireEvent.click(screen.getByRole('button', {name: /cancel/i}));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test('calls onClose when the ✕ button is clicked', () => {
    const {onClose} = renderForm();
    fireEvent.click(screen.getByRole('button', {name: /✕/i}));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test('calls onClose when the backdrop is clicked', () => {
    const {onClose} = renderForm();
    fireEvent.click(document.querySelector('.form-backdrop'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test('disables buttons while submitting', async () => {
    global.fetch = jest.fn(() => new Promise(() => {}));
    renderForm();
    fireEvent.change(screen.getByLabelText(/theme title/i), {target: {name: 'title', value: 'Test'}});
    fireEvent.change(screen.getByLabelText(/why should this be added/i), {target: {name: 'reason', value: 'reason'}});
    fireEvent.click(screen.getByRole('button', {name: /submit request/i}));
    await waitFor(() => {
      expect(screen.getByRole('button', {name: /submitting/i})).toBeDisabled();
      expect(screen.getByRole('button', {name: /cancel/i})).toBeDisabled();
    });
  });
});