import {Dispatch, SetStateAction, useMemo} from 'react'
import {ScatterDot, SpiralThumbnail} from '../../types'
import {Box} from '@chakra-ui/react'
import useDimensions from 'react-cool-dimensions'
import {
  hierarchy as d3Hierarchy,
  HierarchyNode,
  HierarchyRectangularNode,
  treemap as d3treemap,
} from 'd3-hierarchy'
import {spiralTile, spiralStrategy as getK} from './spiral-tile'
import {convert2SpatiallyAwareArray} from './spatial-spiral'
import {
  SPIRAL_MAP,
  SPATIAL_SPIRAL_MAP,
  GRID_LAYOUT,
} from '../../components/neighborhood/constants'
import HtmlImageThumbnail from '../../components/html-image-thumbnail/html-image-thumbnail'

const calculateGridPositions = (
  root: HierarchyRectangularNode<SpiralThumbnail>,
  gridElemSize: number | null,
  numElems: number,
  width: number,
  height: number,
) => {
  let noItemsHorizontal = null,
    noItemsVertical = null
  if (gridElemSize) {
    noItemsHorizontal = width / gridElemSize
    noItemsVertical = height / gridElemSize
  } else {
    noItemsHorizontal = Math.sqrt(numElems + 1)
    noItemsVertical = noItemsHorizontal
  }

  const tileWidth = width / noItemsHorizontal
  const tileHeight = height / noItemsVertical

  let x = 0,
    y = 0
  if (!root.children) return root
  root.children.forEach(child => {
    if (x + tileWidth >= width) {
      x = 0
      y += tileHeight
    }
    child.x0 = x
    child.x1 = child.x0 + tileWidth
    child.y0 = y
    child.y1 = child.y0 + tileHeight
    x += tileWidth
  })

  return root
}

const getId = (d: HierarchyNode<SpiralThumbnail>) =>
  (d.parent ? d.parent.data.id + '.' : '') + d.data.name + '-' + d.data.index

const createRoot = (children: SpiralThumbnail[]) => {
  // to match type definition, but the root is only needed for
  // spawning the hierarchy
  const fakeScatterDotProps = {
    dbId: 0,
    x: 0,
    y: 0,
    lbl: '',
    prd: '',
    uri: '',
    hit: 0,
    ss: '',
    w: 0,
    h: 0,
    ms: 0,
  }
  return {
    ...fakeScatterDotProps,
    name: 'root',
    index: 0,
    children,
  }
}

/**
 * Generate a grid for the thumbnails in the neighborhood.
 *
 *
 * @param data
 * @param width   Container width
 * @param height  Container height
 * @returns
 */
const fetchGridNodes = (
  data: SpiralThumbnail[],
  width: number,
  height: number,
) => {
  let children = data.map(p => ({...p, placeholder: false}))
  const root = createRoot(children)
  const hierarchy = (inputData: SpiralThumbnail) =>
    d3Hierarchy<SpiralThumbnail>(inputData).eachBefore(
      d => (d.data.id = getId(d)),
    )
  let rootNode = hierarchy(root) as HierarchyRectangularNode<SpiralThumbnail>
  rootNode = calculateGridPositions(rootNode, null, data.length, width, height)
  return rootNode.descendants().slice(1)
}

const featchSpiralNodes = (
  data: SpiralThumbnail[],
  layout: string,
  ringStrategy: string,
  maxRings: number,
  width: number,
  height: number,
) => {
  let children = data.map(p => ({...p, placeholder: false}))
  if (layout === SPIRAL_MAP) {
    children = children.map((p, i) => ({...p, k: getK(ringStrategy, i)}))
  } else {
    children = convert2SpatiallyAwareArray(children, maxRings)
  }
  const root = createRoot(children)
  const hierarchyFn = (inputData: SpiralThumbnail) =>
    d3Hierarchy<SpiralThumbnail>(inputData).eachBefore(
      d => (d.data.id = getId(d)),
    )
  const treemap = (hierarchy: HierarchyNode<SpiralThumbnail>) =>
    d3treemap<SpiralThumbnail>()
      .tile(spiralTile)
      .size([width, height])
      .paddingOuter(0)
      .round(false)(hierarchy)
  const newRoot = treemap(
    hierarchyFn(root),
  ) as HierarchyRectangularNode<SpiralThumbnail>
  return newRoot.descendants().slice(1)
}

export interface SpiralMapProps {
  layout: string
  pointInterest: ScatterDot
  neighbors: ScatterDot[]
  selectedIndexes: boolean[]
  setSelectedIndexes: Dispatch<SetStateAction<boolean[]>>
  ringStrategy: string
  maxRings: number
}

export function SpiralMap({
  layout,
  pointInterest,
  neighbors,
  ringStrategy,
  maxRings,
  selectedIndexes,
  setSelectedIndexes,
}: SpiralMapProps) {
  const {observe, width, height} = useDimensions({polyfill: ResizeObserver})

  const breaks = [
    [13, 2],
    [20, 4],
    [51, 12],
    [128, 28],
    [512, 60],
  ]

  const descendants = useMemo<
    HierarchyRectangularNode<SpiralThumbnail>[] | null
  >(() => {
    // create rings here for spiral map
    let newRings: number[] = []
    let ring = 1
    for (let brk of breaks) {
      for (let j = 0; j < brk[0]; j++) newRings.push(ring)
      ring += 1
    }
    newRings[0] = 0

    const transform = (
      image: ScatterDot,
      neighbors: ScatterDot[],
      breaks: number[][],
    ) => {
      // merge image with neighbors and calculate k for spiral
      const collection = [image, ...neighbors]
      let ks: number[] = []

      for (let brk of breaks) for (let j = 0; j < brk[0]; j++) ks.push(brk[1])

      const children: SpiralThumbnail[] = collection.map((d, i) => ({
        ...d,
        name: d.dbId.toString(),
        index: i,
        k: ks[i],
        ring: newRings[i],
      }))
      return children
    }

    const inputData = transform(pointInterest, neighbors, breaks)
    let descendants = null

    if (layout === GRID_LAYOUT) {
      descendants = fetchGridNodes(inputData, width, height)
    } else {
      descendants = featchSpiralNodes(
        inputData,
        layout,
        ringStrategy,
        maxRings,
        width,
        height,
      )
    }

    return descendants
  }, [neighbors, width, height])

  return (
    <Box
      w="full"
      h="full"
      backgroundColor="#2a2a2a"
      pos="relative"
      ref={observe}
    >
      {descendants &&
        descendants.map((d, idx) => (
          <HtmlImageThumbnail
            key={d.data.id}
            imageNode={d}
            objectFit={'fit'}
            selected={selectedIndexes[idx]}
            onSelectThumbnail={() => {
              const indexes = [...selectedIndexes]
              indexes[idx] = !indexes[idx]
              setSelectedIndexes(indexes)
            }}
          />
        ))}
    </Box>
  )
}

export default SpiralMap
