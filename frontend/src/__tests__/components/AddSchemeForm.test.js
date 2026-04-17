import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {useAuth} from '../../context';
import AddSchemeForm from '../../components/AddSchemeForm';

jest.mock('../../context', () => ({useAuth: jest.fn()}));

const mockGetToken = jest.fn().mockResolvedValue('test-token');

const renderForm = (overrides = {}) => {
  useAuth.mockReturnValue({getValidAccessToken: mockGetToken});
  const props = {onClose: jest.fn(), onSuccess: jest.fn(), ...overrides};
  render(<AddSchemeForm {...props} />);
  return props;
};

describe('AddSchemeForm', () => {
  afterEach(() => jest.clearAllMocks());

  test('renders name, description, and template fields', () => {
    renderForm();
    expect(screen.getByLabelText(/scheme name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/template/i)).toBeInTheDocument();
  });

  test('shows validation error when name is empty', async () => {
    renderForm();
    fireEvent.click(screen.getByRole('button', {name: /create scheme/i}));
    expect(await screen.findByText(/name is required/i)).toBeInTheDocument();
    expect(mockGetToken).not.toHaveBeenCalled();
  });

  test('shows validation error when template is empty', async () => {
    renderForm();
    fireEvent.change(screen.getByLabelText(/scheme name/i), {target: {name: 'name', value: 'Analogy'}});
    fireEvent.click(screen.getByRole('button', {name: /create scheme/i}));
    expect(await screen.findByText(/template is required/i)).toBeInTheDocument();
    expect(mockGetToken).not.toHaveBeenCalled();
  });

  test('calls onSuccess after a successful submission', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: true});
    const {onSuccess} = renderForm();
    fireEvent.change(screen.getByLabelText(/scheme name/i), {target: {name: 'name', value: 'Expert Opinion'}});
    fireEvent.change(screen.getByLabelText(/template/i), {target: {name: 'template', value: '**Expert** says **Claim**'}});
    fireEvent.click(screen.getByRole('button', {name: /create scheme/i}));
    await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1));
  });

  test('POSTs the correct form data to the API', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: true});
    renderForm();
    fireEvent.change(screen.getByLabelText(/scheme name/i), {target: {name: 'name', value: 'Analogy'}});
    fireEvent.change(screen.getByLabelText(/description/i), {target: {name: 'description', value: 'Reasoning by comparison'}});
    fireEvent.change(screen.getByLabelText(/template/i), {target: {name: 'template', value: '**A** is like **B**'}});
    fireEvent.click(screen.getByRole('button', {name: /create scheme/i}));
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    const body = JSON.parse(global.fetch.mock.calls[0][1].body);
    expect(body).toEqual({name: 'Analogy', description: 'Reasoning by comparison', template: '**A** is like **B**'});
  });

  test('shows API error message on failed submission', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: false, json: async () => ({name: ['A scheme with this name already exists.']})});
    renderForm();
    fireEvent.change(screen.getByLabelText(/scheme name/i), {target: {name: 'name', value: 'Duplicate'}});
    fireEvent.change(screen.getByLabelText(/template/i), {target: {name: 'template', value: '**X**'}});
    fireEvent.click(screen.getByRole('button', {name: /create scheme/i}));
    expect(await screen.findByText(/a scheme with this name already exists/i)).toBeInTheDocument();
  });

  test('calls onClose when Cancel is clicked', () => {
    const {onClose} = renderForm();
    fireEvent.click(screen.getByRole('button', {name: /cancel/i}));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test('disables buttons while submitting', async () => {
    global.fetch = jest.fn(() => new Promise(() => {}));
    renderForm();
    fireEvent.change(screen.getByLabelText(/scheme name/i), {target: {name: 'name', value: 'Test'}});
    fireEvent.change(screen.getByLabelText(/template/i), {target: {name: 'template', value: '**X**'}});
    fireEvent.click(screen.getByRole('button', {name: /create scheme/i}));
    await waitFor(() => {
      expect(screen.getByRole('button', {name: /creating/i})).toBeDisabled();
      expect(screen.getByRole('button', {name: /cancel/i})).toBeDisabled();
    });
  });
});