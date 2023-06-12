import {render} from '@testing-library/react'

import ColorMultiSelect from './color-multi-select'

describe('ColorMultiSelect', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<ColorMultiSelect />)
    expect(baseElement).toBeTruthy()
  })
})
