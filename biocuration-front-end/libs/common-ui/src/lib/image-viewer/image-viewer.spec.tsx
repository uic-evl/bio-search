import {render} from '@testing-library/react'

import ImageViewer from './image-viewer'

describe('ImageViewer', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<ImageViewer />)
    expect(baseElement).toBeTruthy()
  })
})
