import {render} from '@testing-library/react'

import PanelHeader from './panel-header'

describe('PanelHeader', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<PanelHeader />)
    expect(baseElement).toBeTruthy()
  })
})
