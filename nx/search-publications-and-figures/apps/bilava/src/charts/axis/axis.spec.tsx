import {render} from '@testing-library/react'

import Axis from './axis'

describe('Axis', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<Axis />)
    expect(baseElement).toBeTruthy()
  })
})
