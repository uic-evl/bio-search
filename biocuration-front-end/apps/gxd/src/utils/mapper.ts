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

// const colorsMapper: {[id: string]: string} = {
//   his: '#a6cee3',
//   lin: '#1f78b4',
//   diag: '#b2df8a',
//   mac: '#33a02c',
//   '3ds': '#fb9a99',
//   fluo: '#e31a1c',
//   gelb: '#fdbf6f',
//   pla: '#ff7f00',
//   lig: '#cab2d6',
//   oth: '#6a3d9a',
//   res: '#ffff99',
//   com: '#b15928',
// }

const colorsMapper: {[id: string]: string} = {
  mol: '#a6cee3',
  'mol.pro': '#a6cee3',
  'mol.dna': '#a6cee3',
  'mol.che': '#a6cee3',
  'mol.3ds': '#a6cee3',
  mic: '#1f78b4',
  'mic.lig': '#1f78b4',
  'mic.ele': '#1f78b4',
  'mic.ele.sca': '#1f78b4',
  'mic.ele.tra': '#1f78b4',
  'mic.flu': '#1f78b4',
  rad: '#b2df8a',
  'rad.ang': '#b2df8a',
  'rad.uls': '#b2df8a',
  'rad.cmp': '#b2df8a',
  'rad.xra': '#b2df8a',
  'rad.oth': '#b2df8a',
  pho: '#33a02c',
  'pho.der': '#33a02c',
  'pho.org': '#33a02c',
  oth: '#fb9a99',
  exp: '#e31a1c',
  'exp.pla': '#e31a1c',
  'exp.gel': '#e31a1c',
  'exp.gel.nor': '#e31a1c',
  'exp.gel.rpc': '#e31a1c',
  'exp.gel.wes': '#e31a1c',
  gra: '#fdbf6f',
  'gra.oth': '#fdbf6f',
  'gra.lin': '#fdbf6f',
  'gra.his': '#fdbf6f',
  'gra.sca': '#fdbf6f',
  'gra.flow': '#fdbf6f',
  'gra.3dr': '#fdbf6f',
  'gra.sig': '#fdbf6f',
}

// const namesMapper: {[id: string]: string} = {
//   his: 'histogram',
//   lin: 'line chart',
//   diag: 'other diagram',
//   mac: 'macromolecule sequence',
//   '3ds': '3D structure',
//   fluo: 'fluorescence microscopy',
//   gelb: 'gel blot',
//   pla: 'plate',
//   lig: 'light microscopy',
//   oth: 'other',
//   res: 'residual',
//   com: 'compound',
// }

const namesMapper: {[id: string]: string} = {
  mol: 'molecule',
  'mol.pro': 'mol - protein sequence',
  'mol.dna': 'mol - dna sequence',
  'mol.che': 'mol - chemical structure',
  'mol.3ds': 'mol - 3D structure',
  mic: 'microscopy',
  'mic.lig': 'light microscopy',
  'mic.ele': 'electron microscopy',
  'mic.ele.sca': 'electron scanning microscopy',
  'mic.ele.tra': 'electron transmission microscopy',
  'mic.flu': 'fluorescence microscopy',
  rad: 'radiology',
  'rad.ang': 'rad - angiography',
  'rad.uls': 'rad - ultrasound',
  'rad.cmp': 'rad - CTA/MRI/PET',
  'rad.xra': 'rad - Xrays',
  'rad.oth': 'rad - other',
  pho: 'photography',
  'pho.der': 'photography - dermatology',
  'pho.org': 'photography - organs',
  oth: 'other',
  exp: 'experimental',
  'exp.pla': 'exp - plate',
  'exp.gel': 'exp - gel',
  'exp.gel.nor': 'exp - gel - northern blots',
  'exp.gel.rpc': 'exp - gel - rpc',
  'exp.gel.wes': 'exp - gel - western blots',
  gra: 'graphics',
  'gra.oth': 'gra - others',
  'gra.lin': 'gra - line chart',
  'gra.his': 'gra - histogram',
  'gra.sca': 'gra - scatterplot',
  'gra.flow': 'gra - flowchart',
  'gra.3dr': 'gra - 3d rendering',
  'gra.sig': 'gra - signals & waves',
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
  // codeMapper,
  // reverseNamesMapper,
  ddlSearchOptions,
}