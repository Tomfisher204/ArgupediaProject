import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {useAuth} from '../../context';
import AddArgumentForm from '../../components/AddArgumentForm';

jest.mock('../../context', () => ({useAuth: jest.fn()}));

const mockGetToken = jest.fn().mockResolvedValue('test-token');

const mockSchemes = [
  {id: 1, name: 'Expert Opinion', description: 'Argument from authority', template: '**Expert** says **Claim**', fields: [{id: 1, name: 'Expert'}, {id: 2, name: 'Claim'}], critical_questions: [{id: 10, question: 'Is the expert reliable?'}]},
  {id: 2, name: 'Analogy', description: null, template: '**A** is like **B**', fields: [{id: 3, name: 'A'}, {id: 4, name: 'B'}], critical_questions: []},
];

const setupFetch = () => {
  global.fetch = jest.fn().mockImplementation((url) => {
    if (url.includes('/api/schemes/')) {
      return Promise.resolve({ok: true, json: async () => mockSchemes});
    }
    if (url.includes('/api/arguments/create/')) {
      return Promise.resolve({ok: true, json: async () => ({id: 99})});
    }
    return Promise.resolve({ok: true, json: async () => ({})});
  });
};

const renderInitialForm = (overrides = {}) => {
  useAuth.mockReturnValue({getValidAccessToken: mockGetToken});
  const props = {themeId: 5, parentArgumentId: null, parentSchemeId: null, onClose: jest.fn(), onSuccess: jest.fn(), ...overrides};
  render(<AddArgumentForm {...props} />);
  return props;
};

const renderResponseForm = (overrides = {}) => {
  useAuth.mockReturnValue({getValidAccessToken: mockGetToken});
  const props = {themeId: 5, parentArgumentId: 42, parentSchemeId: 1, onClose: jest.fn(), onSuccess: jest.fn(), ...overrides};
  render(<AddArgumentForm {...props} />);
  return props;
};

describe('AddArgumentForm - initial argument', () => {
  afterEach(() => jest.clearAllMocks());

  test('renders as initial argument form when no parent', async () => {
    setupFetch();
    renderInitialForm();
    await waitFor(() => screen.getByText(/add initial argument/i));
    expect(screen.queryByLabelText(/critical question/i)).not.toBeInTheDocument();
  });

  test('shows loading hint while schemes are fetching', () => {
    useAuth.mockReturnValue({getValidAccessToken: mockGetToken});
    global.fetch = jest.fn(() => new Promise(() => {}));
    renderInitialForm();
    expect(screen.getByText(/loading schemes/i)).toBeInTheDocument();
  });

  test('renders scheme options after fetch', async () => {
    setupFetch();
    renderInitialForm();
    await waitFor(() => screen.getByRole('option', {name: 'Expert Opinion'}));
    expect(screen.getByRole('option', {name: 'Analogy'})).toBeInTheDocument();
  });

  test('shows scheme fields when a scheme is selected', async () => {
    setupFetch();
    renderInitialForm();
    await waitFor(() => screen.getByRole('option', {name: 'Expert Opinion'}));
    fireEvent.change(screen.getByRole('combobox'), {target: {value: '1'}});
    expect(screen.getByLabelText('Expert')).toBeInTheDocument();
    expect(screen.getByLabelText('Claim')).toBeInTheDocument();
  });

  test('shows scheme description as a hint when present', async () => {
    setupFetch();
    renderInitialForm();
    await waitFor(() => screen.getByRole('option', {name: 'Expert Opinion'}));
    fireEvent.change(screen.getByRole('combobox'), {target: {value: '1'}});
    expect(screen.getByText('Argument from authority')).toBeInTheDocument();
  });

  test('shows error when submitting without selecting a scheme', async () => {
    setupFetch();
    renderInitialForm();
    await waitFor(() => screen.getByRole('option', {name: 'Expert Opinion'}));
    fireEvent.click(screen.getByRole('button', {name: /submit argument/i}));
    expect(await screen.findByText(/Select a scheme…/i)).toBeInTheDocument();
  });

  test('calls onSuccess with new argument id on valid submission', async () => {
    setupFetch();
    const {onSuccess} = renderInitialForm();
    await waitFor(() => screen.getByRole('option', {name: 'Expert Opinion'}));
    fireEvent.change(screen.getByRole('combobox'), {target: {value: '1'}});
    fireEvent.click(screen.getByRole('button', {name: /submit argument/i}));
    await waitFor(() => expect(onSuccess).toHaveBeenCalledWith(99));
  });

  test('calls onClose when Cancel is clicked', async () => {
    setupFetch();
    const {onClose} = renderInitialForm();
    await waitFor(() => screen.getByText(/add initial argument/i));
    fireEvent.click(screen.getByRole('button', {name: /cancel/i}));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test('calls onClose when ✕ is clicked', async () => {
    setupFetch();
    const {onClose} = renderInitialForm();
    await waitFor(() => screen.getByText(/add initial argument/i));
    fireEvent.click(screen.getByRole('button', {name: /✕/i}));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});

describe('AddArgumentForm - response', () => {
  afterEach(() => jest.clearAllMocks());

  test('renders as response form with CQ dropdown when parent is set', async () => {
    setupFetch();
    renderResponseForm();
    await waitFor(() => screen.getByText(/add attack/i));
    expect(screen.getAllByText(/critical question/i)[0]).toBeInTheDocument();
  });

  test('populates CQ dropdown with parent scheme critical questions', async () => {
    setupFetch();
    renderResponseForm();
    await waitFor(() => screen.getByRole('option', {name: 'Is the expert reliable?'}));
  });

  test('shows error when submitting without selecting a CQ', async () => {
    setupFetch();
    renderResponseForm();
    await waitFor(() => screen.getByRole('option', {name: 'Expert Opinion'}));
    fireEvent.change(screen.getAllByRole('combobox')[1], {target: {value: '1'}});
    fireEvent.click(screen.getByRole('button', {name: /submit argument/i}));
    expect(await screen.findByText(/Select a critical question…/i)).toBeInTheDocument();
  });

  test('switches to supporting mode when Supporting toggle is clicked', async () => {
    setupFetch();
    renderResponseForm();
    await waitFor(() => screen.getByText(/add attack/i));
    fireEvent.click(screen.getByRole('button', {name: /supporting/i}));
    expect(screen.getByText(/add support/i)).toBeInTheDocument();
  });

  test('POSTs response payload with parent and CQ fields', async () => {
    setupFetch();
    renderResponseForm();
    await waitFor(() => screen.getByRole('option', {name: 'Expert Opinion'}));
    fireEvent.change(screen.getAllByRole('combobox')[0], {target: {value: '10'}});
    fireEvent.change(screen.getAllByRole('combobox')[1], {target: {value: '1'}});
    fireEvent.click(screen.getByRole('button', {name: /submit argument/i}));
    await waitFor(() => expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/arguments/create/'),
      expect.objectContaining({method: 'POST'})
    ));
    const body = JSON.parse(global.fetch.mock.calls.find(([url]) => url.includes('/api/arguments/create/'))[1].body);
    expect(body.parent_argument_id).toBe(42);
    expect(body.critical_question_id).toBe(10);
    expect(body.attacking).toBe(true);
  });
});