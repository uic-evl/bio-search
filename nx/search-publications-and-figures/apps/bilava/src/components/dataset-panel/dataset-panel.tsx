import {useState} from 'react'
import {Box} from '@chakra-ui/react'
import {BoxHeaderAndOptions} from '../panel-header/panel-header'

export interface DatasetPanelProps {
  taxonomy: string
}

const datasetViewOptions = ['taxonomy', 'updates']

export function DatasetPanel(props: DatasetPanelProps) {
  const [datasetView, setDatasetView] = useState('taxonomy')

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
      </Box>
    </>
  )
}

export default DatasetPanel
