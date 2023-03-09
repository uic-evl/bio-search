import {useState} from 'react'
import {Box} from '@chakra-ui/react'
import {BoxHeaderAndOptions} from '../panel-header/panel-header'
import TaxonomyTree from '../../charts/taxonomy-tree/taxonomy-tree'
import {useTreeData} from '../../charts/taxonomy-tree/use-tree-data'
import ChartContainer from '../../charts/chart-container/chart-container'

export interface DatasetPanelProps {
  taxonomy: string
}

const datasetViewOptions = ['taxonomy', 'updates']

export function DatasetPanel(props: DatasetPanelProps) {
  const [datasetView, setDatasetView] = useState('taxonomy')
  const treeData = useTreeData(props.taxonomy)

  return (
    <>
      <Box>
        <BoxHeaderAndOptions
          title={'Dataset'}
          options={datasetViewOptions}
          value={datasetView}
          onChangeFn={setDatasetView}
        />
        <Box h={'450px'} w="full">
          {treeData && datasetView === 'taxonomy' ? (
            <ChartContainer ml={0} mr={20} mt={5} mb={0} useZoom={false}>
              <TaxonomyTree
                name={props.taxonomy}
                data={treeData}
                barHeight={20}
                rowHeight={40}
                leftContainerWidth={20}
                nodeWidth={20}
                nodeRadius={5}
              />
            </ChartContainer>
          ) : null}
        </Box>
      </Box>
    </>
  )
}

export default DatasetPanel
