import {useState} from 'react'
import {Grid, GridItem} from '@chakra-ui/react'
import DatasetPanel from '../../components/dataset-panel/dataset-panel'
import ProjectionPanel from '../../components/projection-panel/projection-panel'
import Neighborhood from '../../components/neighborhood/neighborhood'
import {ScatterDot} from '../../types'

/* eslint-disable-next-line */
export interface ExplorerPageProps {}

export function ExplorerPage(props: ExplorerPageProps) {
  const project = 'cord19'
  const [data, setData] = useState<ScatterDot[]>([])
  const [pointInterest, setPointInterest] = useState<ScatterDot | null>(null)

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
        />
      </GridItem>
      <GridItem area="thumbnails">
        <Neighborhood data={data} pointInterest={pointInterest} />
      </GridItem>
    </Grid>
  )
}

export default ExplorerPage
