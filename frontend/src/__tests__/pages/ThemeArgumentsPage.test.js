import React from 'react';
import {render, screen, fireEvent, waitFor} from '@testing-library/react';
import {useAuth} from '../../context';
import ThemeArgumentsPage from '../../pages/ThemeArgumentsPage';

jest.mock('../../context', () => ({useAuth: jest.fn()}));

jest.mock('react-router-dom', () => ({...jest.requireActual('react-router-dom'), useNavigate: () => jest.fn(), useParams: () => ({themeId: '5'})}));

jest.mock('../../components', () => ({
  Navbar: () => <nav data-testid="navbar" />,
  AddArgumentForm: ({onClose, onSuccess}) => (
    <div data-testid="add-argument-form">
      <button onClick={onSuccess}>Submit</button>
      <button onClick={onClose}>Cancel</button>
    </div>
  ),
}));

const mockThemeData = {
  theme: {id: 5, title: 'Technology Ethics', description: 'Debates about tech.'},
  arguments: [
    {
      id: 1,
      scheme_name: 'Expert Opinion',
      scheme_template: '**Expert** claims **Claim**',
      field_values: [{field_name: 'Expert', value: 'Dr. Wong'}, {field_name: 'Claim', value: 'AI is safe'}],
      author: 'alice',
      child_count: 2
    },
    {
      id: 2,
      scheme_name: 'Analogy',
      scheme_template: null,
      field_values: [{field_name: 'Source', value: 'Cars'}],
      author: 'bob',
      child_count: 0
    }
  ]
};

const setupFetch = (data = mockThemeData) => {
  global.fetch = jest.fn().mockResolvedValue({ok: true, json: async () => data});
};

const renderPage = () => render(<ThemeArgumentsPage />);

describe('ThemeArgumentsPage', () => {
  afterEach(() => jest.clearAllMocks());

  test('shows loading message while fetching', () => {
    useAuth.mockReturnValue({getValidAccessToken: jest.fn()});
    global.fetch = jest.fn(() => new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading arguments/i)).toBeInTheDocument();
  });

  test('shows error message when fetch fails', async () => {
    useAuth.mockReturnValue({getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    global.fetch = jest.fn().mockResolvedValue({ok: false});
    renderPage();
    await waitFor(() => expect(screen.getByText(/failed to load arguments/i)).toBeInTheDocument());
  });

  test('renders theme title and description', async () => {
    useAuth.mockReturnValue({getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => expect(screen.getByText('Technology Ethics')).toBeInTheDocument());
    expect(screen.getByText('Debates about tech.')).toBeInTheDocument();
  });

  test('renders argument cards with scheme and author', async () => {
    useAuth.mockReturnValue({getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => expect(screen.getByText('Expert Opinion')).toBeInTheDocument());
    expect(screen.getByText('Analogy')).toBeInTheDocument();
    expect(screen.getByText(/by alice/i)).toBeInTheDocument();
    expect(screen.getByText(/by bob/i)).toBeInTheDocument();
  });

  test('renders template preview for arguments with a scheme template', async () => {
    useAuth.mockReturnValue({getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText('Expert Opinion'));
    expect(screen.getByText(/dr\. wong/i)).toBeInTheDocument();
    expect(screen.getByText(/ai is safe/i)).toBeInTheDocument();
  });

  test('shows empty state message when no arguments exist', async () => {
    useAuth.mockReturnValue({getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch({theme: {id: 5, title: 'Empty Theme', description: ''}, arguments: []});
    renderPage();
    await waitFor(() => expect(screen.getByText(/no arguments in this theme yet/i)).toBeInTheDocument());
  });

  test('navigates to argument page on card click', async () => {
    const navigate = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(navigate);
    useAuth.mockReturnValue({getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText('Expert Opinion'));
    fireEvent.click(screen.getByText('Expert Opinion').closest('button'));
    expect(navigate).toHaveBeenCalledWith('/arguments/1');
  });

  test('opens AddArgumentForm when Add Initial Argument is clicked', async () => {
    useAuth.mockReturnValue({getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText('Technology Ethics'));
    fireEvent.click(screen.getByRole('button', {name: /add initial argument/i}));
    expect(screen.getByTestId('add-argument-form')).toBeInTheDocument();
  });

  test('closes form and refetches on form success', async () => {
    useAuth.mockReturnValue({getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText('Technology Ethics'));
    fireEvent.click(screen.getByRole('button', {name: /add initial argument/i}));
    fireEvent.click(screen.getByRole('button', {name: /submit/i}));
    await waitFor(() => expect(screen.queryByTestId('add-argument-form')).not.toBeInTheDocument());
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  test('closes form without refetching when cancelled', async () => {
    useAuth.mockReturnValue({getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText('Technology Ethics'));
    fireEvent.click(screen.getByRole('button', {name: /add initial argument/i}));
    const fetchCallsBefore = global.fetch.mock.calls.length;
    fireEvent.click(screen.getByRole('button', {name: /cancel/i}));
    expect(screen.queryByTestId('add-argument-form')).not.toBeInTheDocument();
    expect(global.fetch.mock.calls.length).toBe(fetchCallsBefore);
  });

  test('displays child count on argument cards with responses', async () => {
    useAuth.mockReturnValue({getValidAccessToken: jest.fn().mockResolvedValue('tok')});
    setupFetch();
    renderPage();
    await waitFor(() => screen.getByText(/2 responses/i));
  });
});