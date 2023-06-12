import {render} from '@testing-library/react'

import ThreeScatterplot from './three-scatterplot'

describe('ThreeScatterplot', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<ThreeScatterplot />)
    expect(baseElement).toBeTruthy()
  })
})
