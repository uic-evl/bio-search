import {render} from '@testing-library/react'

import ChartContainer from './chart-container'

describe('ChartContainer', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<ChartContainer />)
    expect(baseElement).toBeTruthy()
  })
})
