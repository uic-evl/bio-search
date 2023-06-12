import {render} from '@testing-library/react'

import FiguresPerPageViewer from './figures-per-page-viewer'

describe('FiguresPerPageViewer', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<FiguresPerPageViewer />)
    expect(baseElement).toBeTruthy()
  })
})
