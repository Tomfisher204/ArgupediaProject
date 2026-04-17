import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {useAuth} from '../../context';
import AddCriticalQuestionForm from '../../components/AddCriticalQuestionForm';

jest.mock('../../context', () => ({useAuth: jest.fn()}));

const mockGetToken = jest.fn().mockResolvedValue('test-token');

const renderForm = (overrides = {}) => {
  useAuth.mockReturnValue({getValidAccessToken: mockGetToken});
  const props = {schemeId: 3, onClose: jest.fn(), onSuccess: jest.fn(), ...overrides};
  render(<AddCriticalQuestionForm {...props} />);
  return props;
};

describe('AddCriticalQuestionForm', () => {
  afterEach(() => jest.clearAllMocks());

  test('renders the question textarea and two-way checkbox', () => {
    renderForm();
    expect(screen.getByLabelText(/critical question/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/is it two-way/i)).toBeInTheDocument();
  });

  test('shows validation error when question is empty', async () => {
    renderForm();
    fireEvent.click(screen.getByRole('button', {name: /create question/i}));
    expect(await screen.findByText(/question is required/i)).toBeInTheDocument();
    expect(mockGetToken).not.toHaveBeenCalled();
  });

  test('calls onSuccess after a successful submission', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: true});
    const {onSuccess} = renderForm();
    fireEvent.change(screen.getByLabelText(/critical question/i), {
      target: {name: 'question', value: 'Is the source reliable?'},
    });
    fireEvent.click(screen.getByRole('button', {name: /create question/i}));
    await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1));
  });

  test('POSTs question, two_way flag, and scheme_id to the API', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: true});
    renderForm({schemeId: 7});
    fireEvent.change(screen.getByLabelText(/critical question/i), {
      target: {name: 'question', value: 'Is the expert credible?'},
    });
    fireEvent.click(screen.getByRole('button', {name: /create question/i}));
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    const body = JSON.parse(global.fetch.mock.calls[0][1].body);
    expect(body).toEqual({question: 'Is the expert credible?', two_way: false, scheme_id: 7});
  });

  test('sends two_way: true when the checkbox is checked', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: true});
    renderForm();
    fireEvent.change(screen.getByLabelText(/critical question/i), {
      target: {name: 'question', value: 'Does this apply both ways?'},
    });
    fireEvent.click(screen.getByRole('checkbox'));
    fireEvent.click(screen.getByRole('button', {name: /create question/i}));
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    const body = JSON.parse(global.fetch.mock.calls[0][1].body);
    expect(body.two_way).toBe(true);
  });

  test('shows API error message on failed submission', async () => {
    global.fetch = jest.fn().mockResolvedValue({ok: false, json: async () => ({question: ['This question already exists.']})});
    renderForm();
    fireEvent.change(screen.getByLabelText(/critical question/i), {
      target: {name: 'question', value: 'Duplicate question?'},
    });
    fireEvent.click(screen.getByRole('button', {name: /create question/i}));
    expect(await screen.findByText(/this question already exists/i)).toBeInTheDocument();
  });

  test('calls onClose when Cancel is clicked', () => {
    const {onClose} = renderForm();
    fireEvent.click(screen.getByRole('button', {name: /cancel/i}));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test('disables buttons while submitting', async () => {
    global.fetch = jest.fn(() => new Promise(() => {}));
    renderForm();
    fireEvent.change(screen.getByLabelText(/critical question/i), {
      target: {name: 'question', value: 'Some question?'},
    });
    fireEvent.click(screen.getByRole('button', {name: /create question/i}));
    await waitFor(() => {
      expect(screen.getByRole('button', {name: /creating/i})).toBeDisabled();
      expect(screen.getByRole('button', {name: /cancel/i})).toBeDisabled();
    });
  });
});