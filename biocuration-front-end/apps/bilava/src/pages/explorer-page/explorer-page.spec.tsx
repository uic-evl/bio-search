import {render} from '@testing-library/react'

import ExplorerPage from './explorer-page'

describe('ExplorerPage', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<ExplorerPage />)
    expect(baseElement).toBeTruthy()
  })
})
