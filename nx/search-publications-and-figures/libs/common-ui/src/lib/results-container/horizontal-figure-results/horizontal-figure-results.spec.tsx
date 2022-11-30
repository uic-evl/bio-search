import {render} from '@testing-library/react'

import HorizontalFigureResults from './horizontal-figure-results'

describe('HorizontalFigureResults', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<HorizontalFigureResults />)
    expect(baseElement).toBeTruthy()
  })
})
