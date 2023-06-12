import { render } from '@testing-library/react';

import RowModalityLegend from './row-modality-legend';

describe('RowModalityLegend', () => {
  it('should render successfully', () => {
    const { baseElement } = render(<RowModalityLegend />);
    expect(baseElement).toBeTruthy();
  });
});
