import {render} from '@testing-library/react'

import SimpleResultCard from './simple-result-card'

describe('SimpleResultCard', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<SimpleResultCard />)
    expect(baseElement).toBeTruthy()
  })
})
