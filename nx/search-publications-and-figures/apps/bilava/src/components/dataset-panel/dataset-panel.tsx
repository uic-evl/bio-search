import {useState} from 'react'
import {Box} from '@chakra-ui/react'
import {BoxHeaderAndOptions} from '../panel-header/panel-header'
import TaxonomyTree from '../../charts/taxonomy-tree/taxonomy-tree'
import {useTreeData} from '../../charts/taxonomy-tree/use-tree-data'

export interface DatasetPanelProps {
  taxonomy: string
}

const datasetViewOptions = ['taxonomy', 'updates']

export function DatasetPanel(props: DatasetPanelProps) {
  const [datasetView, setDatasetView] = useState('taxonomy')
  const treeData = useTreeData(props.taxonomy)

  const onChangeDataview = (value: string | null) => {
    if (value) setDatasetView(value)
  }

  return (
    <>
      <Box>
        <BoxHeaderAndOptions
          title={'Dataset'}
          options={datasetViewOptions}
          value={datasetView}
          onChangeFn={onChangeDataview}
        />
        <Box h={'450px'} w="full">
          {treeData && datasetView === 'taxonomy' ? (
            <TaxonomyTree
              name={props.taxonomy}
              data={treeData}
              barHeight={20}
              rowHeight={40}
              leftContainerWidth={20}
              nodeWidth={20}
              nodeRadius={5}
            />
          ) : null}
        </Box>
      </Box>
    </>
  )
}

export default DatasetPanel
