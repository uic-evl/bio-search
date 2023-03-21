import {useMemo, useState} from 'react'
import {Box} from '@chakra-ui/react'
import {NeighborhoodPanelHeader} from './panel-header'
import {DEFAULT_STRATEGY, SPIRAL_MAP} from './constants'
import {ScatterDot} from '../../types'
import SpiralMap from '../../charts/spiral-map/spiral-map'

export interface NeighborhoodProps {
  data: ScatterDot[] | null
  pointInterest: ScatterDot | null
}

/**
 * Neighborhood panel.
 *
 * State:
 * - numberNeighbors: Maximum number of elements to display on the grid
 *         including the image of interest
 * - layout: any of spiral maps or grid layout as defined in constants
 * - saliency: TODO
 * - strategy: The number of rings and layout have a defined set of strategies,
 *         which include the number of rings and when the size of the thumbnails
 *         get reduced. These strategies were predefined taking into account the
 *         visibility of the elements.
 * - objectFit: CSS property to show either fit or cover for the thumbnail
 * - selectedIndexes: Keeps the state for what neighbors were selected on the
 *         layout. We separate it from the useMemo neighbors to avoid rerenders
 *         and refetching the image content.
 *
 * @param props
 * @returns
 */
export function Neighborhood(props: NeighborhoodProps) {
  const [numberNeighbors, setNumberNeighbors] = useState<number>(32)
  const [layout, setLayout] = useState(SPIRAL_MAP)
  const [saliency, setSaliency] = useState('')
  const [strategy, setStrategy] = useState(DEFAULT_STRATEGY)
  const [maxRings, setMaxRings] = useState(2)
  const [objectFit, setObjectFit] = useState('fit')
  const [selectedIndexes, setSelectedIndexes] = useState<boolean[]>(
    Array.from({length: 32}, () => false),
  )

  const handleSelectAll = () => {}
  const handleDeselectAll = () => {}

  const findNClosestNeighbors = (point: ScatterDot, n: number) => {
    if (!props.data) return []

    const points = props.data.map(d => ({
      ...d,
      distance: Math.pow(d.x - point.x, 2) + Math.pow(d.y - point.y, 2),
      selected: false,
    }))
    points.sort((a, b) => a.distance - b.distance)
    const output = Math.min(points.length - 1, n)
    return points.slice(1, output + 1)
  }

  const neighbors = useMemo<ScatterDot[]>(() => {
    if (!props.pointInterest) return []
    let candidates = findNClosestNeighbors(props.pointInterest, numberNeighbors)

    // update indices
    if (numberNeighbors > selectedIndexes.length) {
      const remaining = Array.from(
        {length: selectedIndexes.length - numberNeighbors},
        () => false,
      )
      setSelectedIndexes(selectedIndexes.concat(remaining))
    } else if (numberNeighbors < selectedIndexes.length) {
      setSelectedIndexes(selectedIndexes.slice(0, numberNeighbors))
    }

    return candidates
  }, [props.pointInterest, numberNeighbors])
  console.log('neighbors', neighbors)

  return (
    <Box h="full">
      <NeighborhoodPanelHeader
        layout={layout}
        setLayout={setLayout}
        strategy={strategy}
        setStrategy={setStrategy}
        saliency={saliency}
        setSaliency={setSaliency}
        setNumberNeighbors={setNumberNeighbors}
        setMaxRings={setMaxRings}
        objectFit={objectFit}
        setObjectFit={setObjectFit}
        onSelectAll={handleSelectAll}
        onDeselectAll={handleDeselectAll}
      />
      {neighbors.length > 0 && props.pointInterest ? (
        <SpiralMap
          pointInterest={props.pointInterest}
          neighbors={neighbors}
          maxRings={maxRings}
          ringStrategy={strategy}
          layout={layout}
          selectedIndexes={selectedIndexes}
          setSelectedIndexes={setSelectedIndexes}
        />
      ) : null}
    </Box>
  )
}

export default Neighborhood
