import {render} from '@testing-library/react'

import LabelUpdater from './label-updater'

describe('LabelUpdater', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<LabelUpdater />)
    expect(baseElement).toBeTruthy()
  })
})
