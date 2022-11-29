import {render} from '@testing-library/react'

import UnauthenticatedApp from './unauthenticated-app'

describe('UnauthenticatedApp', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<UnauthenticatedApp />)
    expect(baseElement).toBeTruthy()
  })
})
