import {render} from '@testing-library/react'

import Annotations from './annotations'

describe('Annotations', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<Annotations />)
    expect(baseElement).toBeTruthy()
  })
})
