import {render} from '@testing-library/react'

import FigureBboxViewer from './figure-bbox-viewer'

describe('FigureBboxViewer', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<FigureBboxViewer />)
    expect(baseElement).toBeTruthy()
  })
})
