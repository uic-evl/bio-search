import {Dispatch, SetStateAction, useRef, useState} from 'react'
import {Box, Flex, IconButton} from '@chakra-ui/react'
import {useSize} from '@chakra-ui/react-use-size'
import {NeighborhoodPanelHeader} from './panel-header'
import {DEFAULT_STRATEGY, SPIRAL_MAP} from './constants'
import {ScatterDot} from '../../types'
import SpiralMap from '../../charts/spiral-map/spiral-map'
import {CloseIcon} from '@chakra-ui/icons'
import ThumbnailDetails from '../thumbnail-details/thumbnail-details'

export interface NeighborhoodProps {
  data: ScatterDot[] | null
  pointInterest: ScatterDot | null
  neighbors: ScatterDot[]
  selectedIndexes: boolean[]
  setNumNeighbors: Dispatch<SetStateAction<number>>
  setNeighborsIdx: Dispatch<SetStateAction<boolean[]>>
  classifier: string
  labels: string[]
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
  // the image to show inside the modal when clicking on a thumbnail
  const [inspectedThumbnail, setInspectedThumbnail] =
    useState<ScatterDot | null>(null)

  const spiralRef = useRef<HTMLDivElement | null>(null)
  const spiralDimensions = useSize(spiralRef)

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
    <Box h="full" w="full">
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
      <Flex
        w="full"
        h="calc(100% - 27px);"
        ref={spiralRef}
        backgroundColor={'blackAlpha.900'}
        justifyContent={'center'}
        alignItems={'center'}
        position="relative"
      >
        {props.neighbors.length > 0 &&
        props.pointInterest &&
        spiralDimensions &&
        spiralDimensions.width > 0 &&
        spiralDimensions.height > 0 ? (
          <SpiralMap
            pointInterest={props.pointInterest}
            neighbors={props.neighbors}
            maxRings={maxRings}
            ringStrategy={strategy}
            layout={layout}
            selectedIndexes={props.selectedIndexes}
            setSelectedIndexes={props.setNeighborsIdx}
            dimensions={{
              width: Math.min(spiralDimensions.width, spiralDimensions.height),
              height: Math.min(spiralDimensions.width, spiralDimensions.height),
            }}
            setInspectedThumbnail={setInspectedThumbnail}
          />
        ) : null}
        {inspectedThumbnail !== null ? (
          <Box
            w="full"
            h="full"
            bg="rgba(255,255,255,0.7)"
            position="absolute"
            top={0}
            left={0}
          >
            <Box position="absolute" top={1} right={1}>
              <IconButton
                aria-label="close"
                icon={<CloseIcon />}
                onClick={() => setInspectedThumbnail(null)}
              />
            </Box>
            <Flex alignItems="center" justifyContent="center" w="full" h="full">
              <Box bg="white" w="90%" h="90%">
                <ThumbnailDetails
                  image={inspectedThumbnail}
                  classifier={props.classifier}
                  labels={props.labels}
                />
              </Box>
            </Flex>
          </Box>
        ) : null}
      </Flex>
    </Box>
  )
}

export default Neighborhood
