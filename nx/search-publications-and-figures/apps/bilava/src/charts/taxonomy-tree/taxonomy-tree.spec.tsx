import {render} from '@testing-library/react'

import TaxonomyTree from './taxonomy-tree'

describe('TaxonomyTree', () => {
  it('should render successfully', () => {
    const {baseElement} = render(<TaxonomyTree />)
    expect(baseElement).toBeTruthy()
  })
})
