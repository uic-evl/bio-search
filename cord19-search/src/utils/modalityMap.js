const Long2Short = {
  histogram: 'his',
  'line chart': 'lin',
  'other diagram': 'diag',
  'macromolecule sequence': 'mac',
  '3D structure': '3ds',
  'fluorescence microscopy': 'fluo',
  'gel blot': 'gelb',
  plate: 'pla',
  'light microscopy': 'lig',
  other: 'oth',
  residual: 'res',
  compound: 'cmp',
}

const Code2Short = {
  0: 'his',
  1: 'lin',
  2: 'diag',
  3: 'mac',
  4: '3ds',
  5: 'flu',
  6: 'gelb',
  7: 'pla',
  8: 'light',
  9: 'other',
  10: 'res',
  11: 'cmp',
}

const Code2Color = {
  0: '#a6cee3',
  1: '#1f78b4',
  2: '#b2df8a',
  3: '#33a02c',
  4: '#fb9a99',
  5: '#e31a1c',
  6: '#fdbf6f',
  7: '#ff7f00',
  8: '#cab2d6',
  9: '#6a3d9a',
  10: '#ffff99',
  11: '#b15928',
}

const Code2Long = {
  0: 'histogram',
  1: 'line chart',
  2: 'other diagram',
  3: 'macromolecule sequence',
  4: '3D structure',
  5: 'fluorescence microscopy',
  6: 'gel blot',
  7: 'plate',
  8: 'light microscopy',
  9: 'other',
  10: 'residual',
  11: 'compound',
}

const Long2Color = {
  histogram: '#a6cee3',
  'line chart': '#1f78b4',
  'other diagram': '#b2df8a',
  'macromolecule sequence': '#33a02c',
  '3D structure': '#fb9a99',
  'fluorescence microscopy': '#e31a1c',
  'gel blot': '#fdbf6f',
  plate: '#ff7f00',
  'light microscopy': '#cab2d6',
  other: '#6a3d9a',
  residual: '#ffff99',
  compound: '#b15928',
}

const Long2ColorCord = {
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

const CordToName = {
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

const modalityOptions = Object.keys(Long2Color).map(x => ({value: x, label: x}))

const cordModalityOptions = Object.keys(CordToName).map(x => ({
  value: x,
  label: x,
}))

export {
  Long2Short,
  Code2Short,
  Code2Color,
  Long2Color,
  Code2Long,
  modalityOptions,
  Long2ColorCord,
  cordModalityOptions,
}
