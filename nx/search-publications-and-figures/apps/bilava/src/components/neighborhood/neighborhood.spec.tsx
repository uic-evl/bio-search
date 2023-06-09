import {render} from '@testing-library/react'

import Neighborhood from './neighborhood'

describe('Neighborhood', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<Neighborhood />)
    expect(baseElement).toBeTruthy()
  })
})
