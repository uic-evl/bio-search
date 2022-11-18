import React from 'react'

import EnhancedSurrogate from '../components/doc_details/enhanced_surrogate'
import data from './sample_data/document.json'

export default {
  title: 'Image Surrogate',
  component: EnhancedSurrogate,
}

export const Document = () => (
  <EnhancedSurrogate document={data} position={1} onClickClose={() => {}} />
)
