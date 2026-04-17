import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';

const fetchMock = jest.fn();
global.fetch = fetchMock;
window.fetch = fetchMock;

const localStorageMock = {
  getItem: jest.fn(() => 'fake-token'),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

jest.mock('../../components', () => ({
  Navbar: () => <nav data-testid="navbar" />,
  TrashIcon: () => <span data-testid="trash-icon" />,
  AddSchemeForm: ({onClose, onSuccess}) => (
    <div>
      <button onClick={onSuccess}>success</button>
      <button onClick={onClose}>close-form</button>
    </div>
  ),
  AddCriticalQuestionForm: ({onClose, onSuccess}) => (
    <div>
      <button onClick={onSuccess}>cq-success</button>
      <button onClick={onClose}>cq-close</button>
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

import AdminSchemes from '../../pages/AdminSchemes';

const mockSchemes = [
  {id: 1, name: 'Scheme A', description: 'Desc A', critical_questions: [{id: 101, question: 'What is A?'}, {id: 102, question: 'Why A?'}]},
  {id: 2, name: 'Scheme B', description: '', critical_questions: []},
];

const setupFetch = () => {
  fetchMock.mockReset();
  fetchMock.mockImplementation((url, options = {}) => {
    const method = options?.method || 'GET';
    const ok = (data) => ({ok: true, status: 200, json: async () => data});
    if (url.includes('/api/admin/schemes/') && method === 'GET') return ok({results: mockSchemes});
    if (url.includes('/api/admin/schemes/') && method === 'DELETE') return ok({});
    if (url.includes('/api/admin/critical-questions/') && method === 'DELETE') return ok({});
    return ok({});
  });
};

const renderPage = () => render(<AdminSchemes />);

describe('AdminSchemes', () => {
  afterEach(() => jest.clearAllMocks());

  test('renders schemes from API', async () => {
    setupFetch();
    renderPage();
    expect(await screen.findByText('Scheme A')).toBeInTheDocument();
    expect(screen.getAllByText('Scheme B')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Critical Questions')[0]).toBeInTheDocument();
  });

  test('opens and closes Add Scheme modal', async () => {
    setupFetch();
    renderPage();
    fireEvent.click(screen.getAllByText('Add New Scheme')[0]);
    const addButtons = await screen.findAllByText('Add New Scheme');
    expect(addButtons[0]).toBeInTheDocument();
    fireEvent.click(screen.getAllByText('close-form')[0]);
    await waitFor(() => {
      expect(screen.queryByText('close-form')).not.toBeInTheDocument();
    });
  });

  test('creates scheme and refreshes list via onSuccess', async () => {
    setupFetch();
    renderPage();
    fireEvent.click(screen.getAllByText('Add New Scheme')[0]);
    fireEvent.click(await screen.findByText('success'));
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/admin/schemes/'), expect.any(Object));
    });
  });

  test('opens and closes Add Critical Question modal', async () => {
    setupFetch();
    renderPage();
    const addButtons = await screen.findAllByText('Add Critical Question');
    fireEvent.click(addButtons[0]);
    expect(await screen.findByText('cq-close')).toBeInTheDocument();
    fireEvent.click(screen.getAllByText('cq-close')[0]);
    await waitFor(() => {
      expect(screen.queryByText('cq-close')).not.toBeInTheDocument();
    });
  });

  test('deletes scheme after confirmation', async () => {
    setupFetch();
    renderPage();
    const deleteButtons = await screen.findAllByText('Delete');
    fireEvent.click(deleteButtons[0]);
    expect(await screen.findByTestId('confirm-dialog')).toBeInTheDocument();
    fireEvent.click(screen.getAllByText('confirm')[0]);
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/admin/schemes/1/'), expect.objectContaining({method: 'DELETE'}));
    });
  });

  test('cancels scheme deletion', async () => {
    setupFetch();
    renderPage();
    const deleteButtons = await screen.findAllByText('Delete');
    fireEvent.click(deleteButtons[0]);
    fireEvent.click(await screen.findByText('cancel'));
    await waitFor(() => {
      expect(screen.queryByTestId('confirm-dialog')).not.toBeInTheDocument();
    });
  });

  test('deletes critical question after confirmation', async () => {
    setupFetch();
    renderPage();
    const trashButtons = await screen.findAllByTestId('trash-icon');
    fireEvent.click(trashButtons[0]);
    expect(await screen.findByTestId('confirm-dialog')).toBeInTheDocument();
    fireEvent.click(screen.getAllByText('confirm')[0]);
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/admin/critical-questions/101/'), expect.objectContaining({method: 'DELETE'}));
    });
  });

  test('handles empty scheme list', async () => {
    fetchMock.mockReset();
    fetchMock.mockImplementation(() => Promise.resolve({ok: true, json: async () => ({results: []})}));
    renderPage();
    await waitFor(() => {
      expect(screen.queryByText('Scheme A')).not.toBeInTheDocument();
    });
  });
});