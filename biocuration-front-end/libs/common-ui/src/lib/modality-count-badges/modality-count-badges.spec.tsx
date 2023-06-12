import {render} from '@testing-library/react'

import ModalityCountBadges from './modality-count-badges'

describe('ModalityCountBadges', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<ModalityCountBadges />)
    expect(baseElement).toBeTruthy()
  })
})
