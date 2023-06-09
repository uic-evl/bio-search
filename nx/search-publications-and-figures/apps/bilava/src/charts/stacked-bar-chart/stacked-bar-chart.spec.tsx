import {render} from '@testing-library/react'

import StackedBarChart from './stacked-bar-chart'

describe('StackedBarChart', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<StackedBarChart />)
    expect(baseElement).toBeTruthy()
  })
})
