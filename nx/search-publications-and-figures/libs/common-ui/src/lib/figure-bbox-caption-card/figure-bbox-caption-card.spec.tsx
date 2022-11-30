import {render} from '@testing-library/react'

import FigureBboxCaptionCard from './figure-bbox-caption-card'

describe('FigureBboxCaptionCard', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<FigureBboxCaptionCard />)
    expect(baseElement).toBeTruthy()
  })
})
