import {render} from '@testing-library/react'

import DatasetPanel from './dataset-panel'

describe('DatasetPanel', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<DatasetPanel />)
    expect(baseElement).toBeTruthy()
  })
})
