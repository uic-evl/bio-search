import {useState, useMemo} from 'react'
import {Grid, GridItem, Box} from '@chakra-ui/react'
import DatasetPanel from '../../components/dataset-panel/dataset-panel'
import ProjectionPanel from '../../components/projection-panel/projection-panel'
import Neighborhood from '../../components/neighborhood/neighborhood'
import {ScatterDot} from '../../types'

import {findNClosestNeighbors} from '../../utils/neighborhood'
import {makeHull, Point} from '../../utils/convex-hull'

/* eslint-disable-next-line */
export interface ExplorerPageProps {}

const INIT_NUM_NEIGHBORS = 32

export function ExplorerPage(props: ExplorerPageProps) {
  const project = 'cord19'
  // data fetched from db
  const [data, setData] = useState<ScatterDot[]>([])
  // neighborhood state
  const [pointInterest, setPointInterest] = useState<ScatterDot | null>(null)
  const [numNeighbors, setNumNeighbors] = useState<number>(INIT_NUM_NEIGHBORS)
  const [neighborsIdx, setNeighborsIdx] = useState<boolean[]>(
    Array.from({length: INIT_NUM_NEIGHBORS + 1}, () => false),
  )

  // neighbors calculated here to allow sharing state between projection and
  // neighborhood views.
  const [neighbors, neighborsConvexHull] = useMemo<
    [ScatterDot[], Point[]]
  >(() => {
    if (!pointInterest) return [[], []]
    const nNeighbors = findNClosestNeighbors(data, pointInterest, 32)
    const hull = makeHull(nNeighbors.map(p => ({x: p.x, y: p.y})))

    // update indices but keep already selected history
    if (numNeighbors > neighborsIdx.length) {
      const length = neighborsIdx.length - numNeighbors
      const remaining = Array.from({length}, () => false)
      setNeighborsIdx(neighborsIdx.concat(remaining))
    } else if (numNeighbors < neighborsIdx.length) {
      setNeighborsIdx(neighborsIdx.slice(0, numNeighbors + 1))
    }

    console.log('hull', hull)
    return [nNeighbors, hull]
  }, [pointInterest, numNeighbors])

  return (
    <Grid
      w="100hv"
      h="100vh"
      gridTemplateColumns={'300px 1fr 1fr'}
      gridTemplateRows={'27px 1fr 300px'}
      gridGap="4px"
      gridTemplateAreas={`"header header header"
      "dataset projection thumbnails"
      "dataset gallery gallery"
      `}
    >
      <GridItem area={'dataset'}>
        <DatasetPanel taxonomy={project} />
      </GridItem>
      <GridItem area="projection">
        <ProjectionPanel
          project={project}
          data={data}
          setData={setData}
          setPointInterest={setPointInterest}
          neighborhoodHull={neighborsConvexHull}
        />
      </GridItem>
      <GridItem area="thumbnails">
        <Neighborhood
          data={data}
          pointInterest={pointInterest}
          neighbors={neighbors}
          selectedIndexes={neighborsIdx}
          setNumNeighbors={setNumNeighbors}
          setNeighborsIdx={setNeighborsIdx}
        />
      </GridItem>
      <GridItem area="gallery">
        <Box w="full" h="full"></Box>
      </GridItem>
    </Grid>
  )
}

export default ExplorerPage
