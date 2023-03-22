import {Dispatch, SetStateAction, useMemo, useState} from 'react'
import {Box} from '@chakra-ui/react'
import {NeighborhoodPanelHeader} from './panel-header'
import {DEFAULT_STRATEGY, SPIRAL_MAP} from './constants'
import {ScatterDot} from '../../types'
import SpiralMap from '../../charts/spiral-map/spiral-map'

export interface NeighborhoodProps {
  data: ScatterDot[] | null
  pointInterest: ScatterDot | null
  neighbors: ScatterDot[]
  selectedIndexes: boolean[]
  setNumNeighbors: Dispatch<SetStateAction<number>>
  setNeighborsIdx: Dispatch<SetStateAction<boolean[]>>
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
  const [layout, setLayout] = useState(SPIRAL_MAP)
  const [saliency, setSaliency] = useState('')
  const [strategy, setStrategy] = useState(DEFAULT_STRATEGY)
  const [maxRings, setMaxRings] = useState(2)
  const [objectFit, setObjectFit] = useState('fit')

  const handleSelectAll = () => {
    let indexes = [...props.selectedIndexes]
    indexes = indexes.map(e => true)
    props.setNeighborsIdx(indexes)
  }
  const handleDeselectAll = () => {
    let indexes = [...props.selectedIndexes]
    indexes = indexes.map(e => false)
    props.setNeighborsIdx(indexes)
  }

  return (
    <Box h="full">
      <NeighborhoodPanelHeader
        layout={layout}
        setLayout={setLayout}
        strategy={strategy}
        setStrategy={setStrategy}
        saliency={saliency}
        setSaliency={setSaliency}
        setNumberNeighbors={props.setNumNeighbors}
        setMaxRings={setMaxRings}
        objectFit={objectFit}
        setObjectFit={setObjectFit}
        onSelectAll={handleSelectAll}
        onDeselectAll={handleDeselectAll}
      />
      {props.neighbors.length > 0 && props.pointInterest ? (
        <SpiralMap
          pointInterest={props.pointInterest}
          neighbors={props.neighbors}
          maxRings={maxRings}
          ringStrategy={strategy}
          layout={layout}
          selectedIndexes={props.selectedIndexes}
          setSelectedIndexes={props.setNeighborsIdx}
        />
      ) : null}
    </Box>
  )
}

export default Neighborhood
