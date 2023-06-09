import {useState, useEffect} from 'react'
import {stratify, hierarchy} from 'd3-hierarchy'
import {rollup} from 'd3-array'

const useTaxonomyTree = (taxonomyList, dbRows, rowHeight, taxonomyName) => {
  const [data, setData] = useState(null)

  const stratifier = stratify()
    .id(d => d[0]) // Map key
    .parentId(d => {
      const i = d[0].lastIndexOf('.')
      // root won't have a '.'
      return i >= 0 ? d[0].slice(0, i) : null
    })

  const createHierarchy = stratifiedElems => {
    let i = 0
    return hierarchy(stratifiedElems)
      .sum(d => d.data[1]) // Map value
      .sort((a, b) => b.height - a.height || a.id - b.id)
      .eachBefore(d => (d.index = i++))
  }

  const createNodes = (taxonomy, dbRows) => {
    // count elements per modality
    const itemsPerGroup = rollup(
      dbRows,
      d => d.length,
      d => d.label,
    )

    // add any missing node to parse tree
    for (let modality of taxonomy) {
      if (itemsPerGroup.get(modality.label) === undefined) {
        itemsPerGroup.set(modality.label, 0)
      }
    }
    // create tree by separating ids by dots
    const tree = stratifier(itemsPerGroup)
    const hierarchy = createHierarchy(tree)

    // DFS to get nodes
    let fringe = [hierarchy]
    let nodes = []

    while (fringe.length > 0) {
      const node = fringe.pop()
      nodes.push(node)

      if (node.children) {
        for (let child of node.children) {
          if (child.children) {
            fringe.push(child)
          }
        }
      }
    }

    let i = 0
    for (let node of nodes) {
      node.expanded = true
      node.y = i * rowHeight
      node.colored = false
      i += 1
    }

    return nodes
  }

  useEffect(() => {
    const formattedRows = dbRows.map(x => ({
      label: `${taxonomyName}.${x}`,
    }))
    const formattedTaxonomy = taxonomyList.map(x => ({
      label: `${taxonomyName}.${x}`,
    }))
    formattedTaxonomy.push({label: taxonomyName})

    const nodes = createNodes(formattedTaxonomy, formattedRows)
    setData(nodes)
  }, [taxonomyList, dbRows, taxonomyName]) // eslint-disable-line

  return [data, setData]
}

export const getTaxonomyHierarchy = (taxonomyList, dbRows, taxonomyName) => {
  const stratifier = stratify()
    .id(d => d[0]) // Map key
    .parentId(d => {
      const i = d[0].lastIndexOf('.')
      // root won't have a '.'
      return i >= 0 ? d[0].slice(0, i) : null
    })

  const createHierarchy = stratifiedElems => {
    let i = 0
    return hierarchy(stratifiedElems)
      .sum(d => d.data[1]) // Map value
      .sort((a, b) => b.height - a.height || a.id - b.id)
      .eachBefore(d => (d.index = i++))
  }

  const createNodes = (taxonomy, dbRows) => {
    // count elements per modality
    const itemsPerGroup = rollup(
      dbRows,
      d => d.length,
      d => d.label,
    )

    // add any missing node to parse tree
    for (let modality of taxonomy) {
      if (itemsPerGroup.get(modality.label) === undefined) {
        itemsPerGroup.set(modality.label, 0)
      }
    }
    // create tree by separating ids by dots
    const tree = stratifier(itemsPerGroup)
    const hierarchy = createHierarchy(tree)
    return hierarchy
  }

  const formattedRows = dbRows.map(x => ({
    label: `${taxonomyName}.${x}`,
  }))
  const formattedTaxonomy = taxonomyList.map(x => ({
    label: `${taxonomyName}.${x}`,
  }))
  formattedTaxonomy.push({label: taxonomyName})

  const nodes = createNodes(formattedTaxonomy, formattedRows)
  return nodes
}

export default useTaxonomyTree
