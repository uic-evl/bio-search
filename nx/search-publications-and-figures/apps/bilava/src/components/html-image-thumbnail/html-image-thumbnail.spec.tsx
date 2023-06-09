import {render} from '@testing-library/react'

import HtmlImageThumbnail from './html-image-thumbnail'

describe('HtmlImageThumbnail', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<HtmlImageThumbnail />)
    expect(baseElement).toBeTruthy()
  })
})
