const namesMapper: {[id: string]: string} = {
  '0': 'his',
  '1': 'lin',
  '2': 'diag',
  '3': 'mac',
  '4': '3ds',
  '5': 'flu',
  '6': 'gelb',
  '7': 'pla',
  '8': 'light',
  '9': 'other',
  '10': 'res',
  '11': 'com',
}

const colorsMapper: {[id: string]: string} = {
  '0': '#a6cee3',
  '1': '#1f78b4',
  '2': '#b2df8a',
  '3': '#33a02c',
  '4': '#fb9a99',
  '5': '#e31a1c',
  '6': '#fdbf6f',
  '7': '#ff7f00',
  '8': '#cab2d6',
  '9': '#6a3d9a',
  '10': '#ffff99',
  '11': '#b15928',
}

// options to popular the search dropdown list
const ddlSearchOptions = Object.keys(colorsMapper).map(x => ({
  value: x,
  label: namesMapper[x],
}))

export {namesMapper, colorsMapper, ddlSearchOptions}
