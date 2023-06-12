import {render} from '@testing-library/react'

import AuthenticatedApp from './authenticated-app'

describe('AuthenticatedApp', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<AuthenticatedApp />)
    expect(baseElement).toBeTruthy()
  })
})
