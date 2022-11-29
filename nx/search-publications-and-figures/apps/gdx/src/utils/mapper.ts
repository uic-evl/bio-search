// mapping for return types from GDX data
const codeMapper: {[id: string]: string} = {
  '0': 'his',
  '1': 'lin',
  '2': 'diag',
  '3': 'mac',
  '4': '3ds',
  '5': 'fluo',
  '6': 'gelb',
  '7': 'pla',
  '8': 'lig',
  '9': 'oth',
  '10': 'res',
  '11': 'com',
}

const colorsMapper: {[id: string]: string} = {
  his: '#a6cee3',
  lin: '#1f78b4',
  diag: '#b2df8a',
  mac: '#33a02c',
  '3ds': '#fb9a99',
  fluo: '#e31a1c',
  gelb: '#fdbf6f',
  pla: '#ff7f00',
  lig: '#cab2d6',
  oth: '#6a3d9a',
  res: '#ffff99',
  com: '#b15928',
}

const namesMapper: {[id: string]: string} = {
  his: 'histogram',
  lin: 'line chart',
  diag: 'other diagram',
  mac: 'macromolecule sequence',
  '3ds': '3D structure',
  fluo: 'fluorescence microscopy',
  gelb: 'gel blot',
  pla: 'plate',
  lig: 'light microscopy',
  oth: 'other',
  res: 'residual',
  com: 'compound',
}

const reverseNamesMapper: {[id: string]: string} = {
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

// options to popular the search dropdown list
const ddlSearchOptions = Object.keys(colorsMapper).map(x => ({
  value: x,
  label: namesMapper[x],
}))

export {
  namesMapper,
  colorsMapper,
  codeMapper,
  reverseNamesMapper,
  ddlSearchOptions,
}
