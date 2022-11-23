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
  compound: 'com',
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
  11: 'com',
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

const modalityOptions = Object.keys(Long2Color).map(x => ({value: x, label: x}))

export {
  Long2Short,
  Code2Short,
  Code2Color,
  Long2Color,
  Code2Long,
  modalityOptions,
}
