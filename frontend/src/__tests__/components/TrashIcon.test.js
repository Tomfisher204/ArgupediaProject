import React from 'react';
import {render} from '@testing-library/react';
import TrashIcon from '../../components/TrashIcon';

describe('TrashIcon', () => {
  test('renders an SVG element', () => {
    const {container} = render(<TrashIcon />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  test('defaults to 16x16 size', () => {
    const {container} = render(<TrashIcon />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveAttribute('width', '16');
    expect(svg).toHaveAttribute('height', '16');
  });

  test('applies a custom size prop', () => {
    const {container} = render(<TrashIcon size={24} />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveAttribute('width', '24');
    expect(svg).toHaveAttribute('height', '24');
  });

  test('defaults stroke color to currentColor', () => {
    const {container} = render(<TrashIcon />);
    const path = container.querySelector('path');
    expect(path).toHaveAttribute('stroke', 'currentColor');
  });

  test('applies a custom color prop to the stroke', () => {
    const {container} = render(<TrashIcon color="#ff0000" />);
    const path = container.querySelector('path');
    expect(path).toHaveAttribute('stroke', '#ff0000');
  });
});