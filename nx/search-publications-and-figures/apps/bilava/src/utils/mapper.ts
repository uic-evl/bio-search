import {schemeCategory10} from 'd3-scale-chromatic'

const colorsMapper: {[id: string]: string} = {
  exp: schemeCategory10[0],
  'exp.pla': schemeCategory10[2],
  'exp.gel': schemeCategory10[3],
  'exp.gel.nor': schemeCategory10[4],
  'exp.gel.rpc': schemeCategory10[5],
  'exp.gel.wes': schemeCategory10[6],
  gra: schemeCategory10[1],
  'gra.oth': schemeCategory10[2],
  'gra.lin': schemeCategory10[3],
  'gra.his': schemeCategory10[4],
  'gra.sca': schemeCategory10[5],
  'gra.flow': schemeCategory10[6],
  'gra.3dr': schemeCategory10[8],
  'gra.sig': schemeCategory10[9],
  mic: schemeCategory10[2],
  'mic.lig': schemeCategory10[3],
  'mic.ele': schemeCategory10[4],
  'mic.ele.sca': schemeCategory10[6],
  'mic.ele.tra': schemeCategory10[8],
  'mic.flu': schemeCategory10[5],
  mol: schemeCategory10[3],
  'mol.pro': schemeCategory10[4],
  'mol.dna': schemeCategory10[5],
  'mol.che': schemeCategory10[6],
  'mol.3ds': schemeCategory10[8],
  pho: schemeCategory10[4],
  'pho.der': schemeCategory10[0],
  'pho.org': schemeCategory10[1],
  rad: schemeCategory10[5],
  'rad.ang': schemeCategory10[0],
  'rad.uls': schemeCategory10[1],
  'rad.cmp': schemeCategory10[2],
  'rad.xra': schemeCategory10[3],
  'rad.oth': schemeCategory10[4],
  oth: schemeCategory10[6],
  unl: schemeCategory10[7],
}

const findChildren = (mapping: Record<string, string>, v: string) => {
  const vSplit = v.split('.')
  const vDepth = vSplit.length

  const children = Object.keys(mapping).filter(
    key => key.includes(v) && key.split('.').length === vDepth + 1,
  )
  return children
}

const isHigherModality = (depth: number) => depth === 1

export const findSiblings = (mapping: Record<string, string>, v: string) => {
  if (!v) return []

  const vSplit = v.split('.')
  const vDepth = vSplit.length

  let siblings = null
  if (!isHigherModality(vDepth)) {
    siblings = Object.keys(mapping).filter(
      key =>
        key !== v &&
        key.split('.').length === vDepth &&
        key.includes(vSplit[0]),
    )
  } else {
    siblings = Object.keys(mapping).filter(
      key => key.split('.').length === 1 && key !== v,
    )
  }
  return siblings
}

export {colorsMapper, findChildren}
