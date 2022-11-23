const namesMapper: {[id: string]: string} = {
  mol: 'molecule',
  'mol.pro': 'mol - protein sequence',
  'mol.dna': 'mol - dna sequence',
  'mol.che': 'mol - chemical structure',
  mic: 'microscopy',
  'mic.lig': 'light microscopy',
  'mic.ele': 'electron microscopy',
  'mic.flu': 'fluorescence microscopy',
  rad: 'radiology',
  'rad.ang': 'rad - angiography',
  'rad.uls': 'rad - ultrasound',
  'rad.cmp': 'rad - CTA/MRI/PET',
  'rad.xra': 'rad - Xrays',
  pho: 'photography',
  oth: 'other',
  exp: 'experimental',
  'exp.pla': 'exp - plate',
  'exp.gel': 'exp - gel',
  gra: 'graphics',
  'gra.oth': 'gra - others',
  'gra.lin': 'gra - line chart',
  'gra.his': 'gra - histogram',
  'gra.sca': 'gra - scatterplot',
}

const colorsMapper: {[id: string]: string} = {
  mol: '#a6cee3',
  'mol.pro': '#a6cee3',
  'mol.dna': '#a6cee3',
  'mol.che': '#a6cee3',
  mic: '#1f78b4',
  'mic.lig': '#1f78b4',
  'mic.ele': '#1f78b4',
  'mic.flu': '#1f78b4',
  rad: '#b2df8a',
  'rad.ang': '#b2df8a',
  'rad.uls': '#b2df8a',
  'rad.cmp': '#b2df8a',
  'rad.xra': '#b2df8a',
  pho: '#33a02c',
  oth: '#fb9a99',
  exp: '#e31a1c',
  'exp.pla': '#e31a1c',
  'exp.gel': '#e31a1c',
  gra: '#fdbf6f',
  'gra.oth': '#fdbf6f',
  'gra.lin': '#fdbf6f',
  'gra.his': '#fdbf6f',
  'gra.sca': '#fdbf6f',
}

// options to popular the search dropdown list
const ddlSearchOptions = Object.keys(colorsMapper).map(x => ({
  value: x,
  label: namesMapper[x],
}))

export {namesMapper, colorsMapper, ddlSearchOptions}
