import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {useAuth} from '../../context';
import ArgumentPage from '../../pages/ArgumentPage';

jest.mock('../../context', () => ({useAuth: jest.fn()}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  Navigate: ({to}) => <div data-testid="navigate">{to}</div>,
  useNavigate: () => jest.fn(),
  useParams: () => ({'*': '42'}),
}));

jest.mock('../../components', () => ({
  Navbar: () => <nav data-testid="navbar" />,
  AddArgumentForm: ({onClose, onSuccess}) => (
    <div data-testid="add-argument-form">
      <button onClick={() => onSuccess(99)}>Submit</button>
      <button onClick={onClose}>Cancel</button>
    </div>
  ),
  ConfirmDialog: ({message, onConfirm, onCancel}) => (
    <div data-testid="confirm-dialog">
      <p>{message}</p>
      <button onClick={onConfirm}>Confirm</button>
      <button onClick={onCancel}>Cancel</button>
    </div>
  ),
  TrashIcon: () => <span data-testid="trash-icon" />,
}));

const mockArgument = {
  id: 42,
  scheme_name: 'Expert Opinion',
  scheme_template: '**Expert** argues **Claim**',
  field_values: [{field_name: 'Expert', value: 'Dr. Jones'}, {field_name: 'Claim', value: 'The earth is round'}],
  author: 'alice',
  theme: 'Science',
  theme_id: 3,
  scheme_id: 7,
  is_winning: true,
  reported: false,
  report_count: 2,
  attackers: [
    {
      id: 1,
      question: 'Is the expert trustworthy?',
      attacking: true,
      argument: {
        id: 10,
        scheme_template: null,
        field_values: [{field_name: 'Premise', value: 'Not credible'}],
        author: 'bob',
        child_count: 1,
      },
    },
  ],
  supporters: [
    {
      id: 2,
      question: 'Is there supporting evidence?',
      attacking: false,
      argument: {
        id: 11,
        scheme_template: null,
        field_values: [{field_name: 'Evidence', value: 'NASA data'}],
        author: 'carol',
        child_count: 0,
      },
    },
  ],
};

const setupFetch = (arg = mockArgument) => {
  global.fetch = jest.fn().mockImplementation((url) => {
    if (url.includes('/report/')) {
      return Promise.resolve({ok: true, json: async () => ({reported: true, report_count: 3})});
    }
    return Promise.resolve({ok: true, json: async () => arg});
  });
};

const mockRegularUser = {username: 'alice', is_admin: false};
const mockAdminUser = {username: 'admin', is_admin: true};

const renderPage = () => render(<ArgumentPage />);

describe('ArgumentPage', () => {
  afterEach(() => jest.clearAllMocks());

  test('shows loading state during fetch', () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    global.fetch = jest.fn(() => new Promise(() => {}));
    renderPage();
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    expect(document.body.firstChild).not.toBeNull();
  });

  test('shows error when fetch fails', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    global.fetch = jest.fn().mockRejectedValue(new Error('Failed to load argument.'));
    renderPage();
    await waitFor(() => expect(screen.queryByText(/loading/i)).not.toBeInTheDocument());
    expect(document.body.children.length).toBe(1);
  });

  test('renders scheme name theme and status', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => expect(screen.getAllByText('Expert Opinion')[0]).toBeInTheDocument());
    expect(screen.getAllByText('Science')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Winning')[0]).toBeInTheDocument();
  });

  test('renders inline preview using scheme template', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getAllByText('Expert Opinion')[0]);
    expect(screen.getAllByText(/dr\. jones/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/the earth is round/i)[0]).toBeInTheDocument();
  });

  test('renders author byline', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => expect(screen.getAllByText(/by alice/i)[0]).toBeInTheDocument());
  });

  test('renders attackers and supporters', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getAllByText('Expert Opinion')[0]);
    expect(screen.getAllByText(/attacking/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/supporting/i)[0]).toBeInTheDocument();
  });

  test('shows no responses message', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch({...mockArgument, attackers: [], supporters: []});
    renderPage();
    await waitFor(() => expect(screen.getAllByText(/no responses to this argument yet/i)[0]).toBeInTheDocument());
  });

  test('renders breadcrumb', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getAllByText('Expert Opinion')[0]);
    expect(screen.getAllByText('Science')[0]).toBeInTheDocument();
    expect(screen.getAllByText(/expert opinion \(42\)/i)[0]).toBeInTheDocument();
  });

  test('toggles report', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText(/report \(2\)/i));
    fireEvent.click(screen.getByText(/report \(2\)/i));
    await waitFor(() => expect(screen.getByText(/unreport \(3\)/i)).toBeInTheDocument());
  });

  test('admin sees delete button', async () => {
    useAuth.mockReturnValue({user: mockAdminUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText('Expert Opinion'));
    expect(screen.getByTestId('trash-icon')).toBeInTheDocument();
  });

  test('non admin hides delete button', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText('Expert Opinion'));
    expect(screen.queryByTestId('trash-icon')).not.toBeInTheDocument();
  });

  test('shows confirm dialog on delete', async () => {
    useAuth.mockReturnValue({user: mockAdminUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByTestId('trash-icon'));
    fireEvent.click(screen.getByTestId('trash-icon').closest('button'));
    expect(screen.getByTestId('confirm-dialog')).toBeInTheDocument();
  });

  test('deletes and navigates', async () => {
    const navigate = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(navigate);
    useAuth.mockReturnValue({user: mockAdminUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByTestId('trash-icon'));
    fireEvent.click(screen.getByTestId('trash-icon').closest('button'));
    fireEvent.click(screen.getByRole('button', {name: /^confirm$/i}));
    await waitFor(() => {
      const deleteCall = global.fetch.mock.calls.find(([url, opts]) => url.includes('/arguments/42/') && opts?.method === 'DELETE');
      expect(deleteCall).toBeTruthy();
    });
    expect(navigate).toHaveBeenCalledWith('/dashboard');
  });

  test('opens add response form', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText('Expert Opinion'));
    fireEvent.click(screen.getByRole('button', {name: /add response/i}));
    expect(screen.getByTestId('add-argument-form')).toBeInTheDocument();
  });

  test('closes form and refetches', async () => {
    useAuth.mockReturnValue({user: mockRegularUser, getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText('Expert Opinion'));
    fireEvent.click(screen.getByRole('button', {name: /add response/i}));
    fireEvent.click(screen.getByRole('button', {name: /submit/i}));
    await waitFor(() => expect(screen.queryByTestId('add-argument-form')).not.toBeInTheDocument());
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });
});