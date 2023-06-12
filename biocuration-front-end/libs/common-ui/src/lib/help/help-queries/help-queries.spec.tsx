import {render} from '@testing-library/react'

import HelpQueries from './help-queries'

describe('HelpQueries', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<HelpQueries />)
    expect(baseElement).toBeTruthy()
  })
})
