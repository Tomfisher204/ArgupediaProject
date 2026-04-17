import React from 'react';
import {render, screen, fireEvent} from '@testing-library/react';
import ConfirmDialog from '../../components/ConfirmDialog';

const renderDialog = (overrides = {}) => {
  const props = {message: 'Are you sure?', onConfirm: jest.fn(), onCancel: jest.fn(), ...overrides};
  render(<ConfirmDialog {...props} />);
  return props;
};

describe('ConfirmDialog', () => {
  afterEach(() => jest.clearAllMocks());

  test('renders the message prop', () => {
    renderDialog({message: 'Delete this item?'});
    expect(screen.getByText('Delete this item?')).toBeInTheDocument();
  });

  test('calls onConfirm when Confirm button is clicked', () => {
    const {onConfirm} = renderDialog();
    fireEvent.click(screen.getByRole('button', {name: /confirm/i}));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  test('calls onCancel when Cancel button is clicked', () => {
    const {onCancel} = renderDialog();
    fireEvent.click(screen.getByRole('button', {name: /cancel/i}));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  test('calls onCancel when the backdrop is clicked', () => {
    const {onCancel} = renderDialog();
    fireEvent.click(document.querySelector('.confirm-backdrop'));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  test('does not call onCancel when the dialog box itself is clicked', () => {
    const {onCancel} = renderDialog();
    fireEvent.click(document.querySelector('.confirm-dialog'));
    expect(onCancel).not.toHaveBeenCalled();
  });

  test('renders both Confirm and Cancel buttons', () => {
    renderDialog();
    expect(screen.getByRole('button', {name: /confirm/i})).toBeInTheDocument();
    expect(screen.getByRole('button', {name: /cancel/i})).toBeInTheDocument();
  });
});