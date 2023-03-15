import {Dispatch, SetStateAction, useState} from 'react'
import {Box, Spacer, Spinner} from '@chakra-ui/react'
import {
  ActionButton,
  HeaderSelect,
  HeaderTitle,
  PanelHeader,
} from '../panel-header/panel-header'
import {useClassifiers} from './use-classifiers'
import ThreeScatterplot from '../../charts/three-scatterplot/three-scatterplot'
import {ScatterDot} from '../../types'
import {fetch_projections} from '../../api'

// const data: ScatterDot[] = [
//   {x: 10, y: 10, lbl: 'exp.gel', prd: 'exp.gel'},
//   {x: 20, y: 20, lbl: 'exp.pla', prd: 'exp.pla'},
// ]

export interface ProjectionPanelProps {
  project: string
}

export function ProjectionPanel(props: ProjectionPanelProps) {
  const [data, setData] = useState<ScatterDot[] | null>(null)
  const [classifier, setClassifier] = useState<string>('')
  const [projection, setProjection] = useState<string>('tsne')
  const [splitSet, setSplitSet] = useState<string>('TRAIN')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const classifiers = useClassifiers(props.project)

  const handleOnLoadData = async () => {
    const projections = await fetch_projections(
      classifier,
      projection,
      splitSet,
    )
    setData(projections)
  }

  return (
    <Box w="full" h="full">
      <ProjectionPanelHeader
        classifiers={classifiers}
        selectedClassifier={classifier}
        setClassifier={setClassifier}
        selectedProjection={projection}
        setProjection={setProjection}
        selectedPartition={splitSet}
        setPartition={setSplitSet}
        isLoading={isLoading}
        onClick={handleOnLoadData}
      />
      <Box w="full" h="full">
        {data ? (
          <ThreeScatterplot data={data} width={800} height={800} />
        ) : null}
      </Box>
    </Box>
  )
}

interface ProjectionPanelHeaderProps {
  classifiers: string[]
  selectedClassifier: string
  setClassifier: Dispatch<SetStateAction<string>>
  selectedProjection: string
  setProjection: Dispatch<SetStateAction<string>>
  selectedPartition: string
  setPartition: Dispatch<SetStateAction<string>>
  isLoading: boolean
  onClick: () => Promise<void>
}

const ProjectionPanelHeader = (props: ProjectionPanelHeaderProps) => {
  const projections = ['pca', 'tsne', 'umap']
  const partitions = ['TRAIN', 'VAL', 'TEST', 'UNL']

  return (
    <Box>
      <PanelHeader>
        <HeaderTitle>Projections</HeaderTitle>
        {props.classifiers.length > 0 ? (
          <HeaderSelect
            placeholder="classifier"
            value={props.selectedClassifier}
            options={props.classifiers}
            onChangeFn={props.setClassifier}
          />
        ) : (
          <Spinner />
        )}
        <HeaderSelect
          placeholder="projection"
          value={props.selectedProjection}
          options={projections}
          onChangeFn={props.setProjection}
        />
        <HeaderSelect
          placeholder="partition"
          value={props.selectedPartition}
          options={partitions}
          onChangeFn={props.setPartition}
        />
        <Spacer />
        <Box>
          <ActionButton
            disabled={
              !props.selectedClassifier ||
              !props.selectedProjection ||
              !props.selectedPartition ||
              props.isLoading
            }
            onClick={props.onClick}
            isLoading={props.isLoading}
          >
            Load
          </ActionButton>
        </Box>
      </PanelHeader>
    </Box>
  )
}

export default ProjectionPanel
