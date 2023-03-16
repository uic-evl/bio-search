import {Grid, GridItem} from '@chakra-ui/react'
import DatasetPanel from '../../components/dataset-panel/dataset-panel'
import ProjectionPanel from '../../components/projection-panel/projection-panel'

/* eslint-disable-next-line */
export interface ExplorerPageProps {}

export function ExplorerPage(props: ExplorerPageProps) {
  const project = 'cord19'

  return (
    <Grid
      w="100hv"
      h="100vh"
      gridTemplateColumns={'300px 1fr 1fr'}
      gridTemplateRows={'27px 1fr 300px'}
      gridGap="1px"
      gridTemplateAreas={`"header header header"
      "dataset projection thumbnails"
      "dataset gallery gallery"
      `}
    >
      <GridItem area={'dataset'}>
        <DatasetPanel taxonomy={project} />
      </GridItem>
      <GridItem area="projection">
        <ProjectionPanel project={project} />
      </GridItem>
    </Grid>
  )
}

export default ExplorerPage
