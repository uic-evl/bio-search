import {render} from '@testing-library/react'

import ThumbnailDetails from './thumbnail-details'

describe('ThumbnailDetails', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<ThumbnailDetails />)
    expect(baseElement).toBeTruthy()
  })
})
