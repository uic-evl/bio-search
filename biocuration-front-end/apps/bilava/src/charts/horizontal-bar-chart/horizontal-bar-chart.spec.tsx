import {render} from '@testing-library/react'

import HorizontalBarChart from './horizontal-bar-chart'

describe('HorizontalBarChart', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<HorizontalBarChart />)
    expect(baseElement).toBeTruthy()
  })
})
