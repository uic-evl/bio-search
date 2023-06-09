import {render} from '@testing-library/react'

import ProjectionPanel from './projection-panel'

describe('ProjectionPanel', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<ProjectionPanel />)
    expect(baseElement).toBeTruthy()
  })
})
