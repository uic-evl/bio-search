import {render} from '@testing-library/react'

import PageThumbnailViewer from './page-thumbnail-viewer'

describe('PageThumbnailViewer', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<PageThumbnailViewer />)
    expect(baseElement).toBeTruthy()
  })
})
