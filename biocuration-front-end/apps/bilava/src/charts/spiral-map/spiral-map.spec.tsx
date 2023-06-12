import {render} from '@testing-library/react'

import SpiralMap from './spiral-map'

describe('SpiralMap', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<SpiralMap />)
    expect(baseElement).toBeTruthy()
  })
})
