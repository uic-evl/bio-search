import {useState, useMemo} from 'react'
import {Grid, GridItem, Box} from '@chakra-ui/react'
import DatasetPanel from '../../components/dataset-panel/dataset-panel'
import ProjectionPanel from '../../components/projection-panel/projection-panel'
import Neighborhood from '../../components/neighborhood/neighborhood'
import {Gallery} from '../../components/gallery/gallery'

import {Filter, ScatterDot} from '../../types'

import {findNClosestNeighbors} from '../../utils/neighborhood'
import {makeHull, Point} from '../../utils/convex-hull'
import Filters from '../../components/filters/filters'

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
  const [galleryIdx, setGalleryIdx] = useState<boolean[]>([])
  const [brushedData, setBrushedData] = useState<ScatterDot[]>([])
  const [filters, setFilters] = useState<Filter>({
    hits: 0.5,
    label: [],
    prediction: [],
    probability: [],
    source: [],
  })
  console.log('filters', filters)

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
      h="99vh"
      gridTemplateColumns={'300px 1fr 1fr'}
      gridTemplateRows={'25px 1fr 300px'}
      gridGap="0px"
      gridTemplateAreas={`"header header header"
      "dataset projection thumbnails"
      "dataset gallery gallery"
      `}
    >
      <GridItem area={'dataset'} borderRight={'1px solid black'}>
        <DatasetPanel taxonomy={project} />
        <Filters data={data} filters={filters} setFilters={setFilters} />
      </GridItem>
      <GridItem area="projection">
        <ProjectionPanel
          project={project}
          data={data}
          setData={setData}
          setPointInterest={setPointInterest}
          neighborhoodHull={neighborsConvexHull}
          setBrushedData={setBrushedData}
          filters={filters}
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
        <Gallery
          data={data}
          size={120}
          selectedIndexes={[]}
          brushedData={brushedData}
          setGalleryIdx={setGalleryIdx}
          setPointInterest={setPointInterest}
        />
      </GridItem>
    </Grid>
  )
}

export default ExplorerPage
