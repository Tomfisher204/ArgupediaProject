import React from 'react';
import {render, screen, fireEvent} from '@testing-library/react';
import {useAuth} from '../../context';
import Navbar from '../../components/Navbar';

jest.mock('../../context', () => ({useAuth: jest.fn()}));

const mockNavigate = jest.fn();
const mockLocation = {pathname: '/dashboard'};

jest.mock('react-router-dom', () => ({...jest.requireActual('react-router-dom'), useNavigate: () => mockNavigate, useLocation: () => mockLocation}));

const renderNavbar = (userOverrides = {}) => {
  useAuth.mockReturnValue({logout: jest.fn(), user: {is_admin: false, ...userOverrides}});
  render(<Navbar />);
};

describe('Navbar', () => {
  afterEach(() => jest.clearAllMocks());

  test('renders the Themes nav link', () => {
    renderNavbar();
    expect(screen.getByRole('button', {name: /themes/i})).toBeInTheDocument();
  });

  test('hides the Schemes link for non-admin users', () => {
    renderNavbar({is_admin: false});
    expect(screen.queryByRole('button', {name: /schemes/i})).not.toBeInTheDocument();
  });

  test('shows the Schemes link for admin users', () => {
    renderNavbar({is_admin: true});
    expect(screen.getByRole('button', {name: /schemes/i})).toBeInTheDocument();
  });

  test('navigates to /dashboard when logo is clicked', () => {
    renderNavbar();
    fireEvent.click(screen.getByText('argupedia'));
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  test('navigates to /themes when Themes is clicked', () => {
    renderNavbar();
    fireEvent.click(screen.getByRole('button', {name: /themes/i}));
    expect(mockNavigate).toHaveBeenCalledWith('/themes');
  });

  test('navigates to /admin/schemes when Schemes is clicked by admin', () => {
    renderNavbar({is_admin: true});
    fireEvent.click(screen.getByRole('button', {name: /schemes/i}));
    expect(mockNavigate).toHaveBeenCalledWith('/admin/schemes');
  });

  test('calls logout when Log out is clicked', () => {
    const logout = jest.fn();
    useAuth.mockReturnValue({logout, user: {is_admin: false}});
    render(<Navbar />);
    fireEvent.click(screen.getByRole('button', {name: /log out/i}));
    expect(logout).toHaveBeenCalledTimes(1);
  });

  test('marks the current route link as active', () => {
    mockLocation.pathname = '/themes';
    renderNavbar();
    expect(screen.getByRole('button', {name: /themes/i})).toHaveClass('active');
  });
});